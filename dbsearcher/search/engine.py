"""
Hyper-optimized search engine with parallel processing.

The core search coordinator that orchestrates file parsing,
result aggregation, and parallel execution for maximum throughput.
"""

import concurrent.futures
import time
import typing

import dbsearcher.exceptions
import dbsearcher.logging
import dbsearcher.search.indexer
import dbsearcher.search.parsers
import dbsearcher.types


@typing.final
class SearchEngine:
    """
    High-performance search engine with parallel processing.

    Provides streaming and parallel search capabilities with
    automatic parser selection and result aggregation.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = (
        "_config",
        "_indexer",
        "_logger",
        "_result_cache",
    )

    def __init__(
        self,
        config: dbsearcher.types.SearchConfig | None = None,
    ) -> None:
        """
        Initialize the search engine.

        Parameters
        ----------
        config
            Search configuration. Uses defaults if not provided.
        """
        self._config: typing.Final[dbsearcher.types.SearchConfig] = (
            config or dbsearcher.types.SearchConfig()
        )
        self._indexer: typing.Final[dbsearcher.search.indexer.FileIndexer] = (
            dbsearcher.search.indexer.FileIndexer(
                self._config.base_dir,
                extensions=self._config.supported_extensions,
            )
        )
        self._logger: typing.Final[dbsearcher.logging.DBSearcherLogger] = (
            dbsearcher.logging.get_logger()
        )
        # LRU cache for repeated queries
        self._result_cache: dict[str, dbsearcher.types.SearchResultList] = {}

    def _search_file(
        self,
        file_info: dbsearcher.types.FileInfo,
        query: str,
    ) -> dbsearcher.types.SearchResultList:
        """
        Search a single file for the query.

        Parameters
        ----------
        file_info
            File metadata.
        query
            Search query string.

        Returns
        -------
        list[SearchResult]
            List of results from this file.
        """
        results: dbsearcher.types.SearchResultList = []

        try:
            parser: dbsearcher.search.parsers.BaseParser = (
                dbsearcher.search.parsers.get_parser_for_file(file_info.path)
            )

            # Get the correct parse method based on parser type
            if isinstance(parser, dbsearcher.search.parsers.TextParser):
                result_iter: dbsearcher.types.SearchResultIterator = parser.parse(
                    file_info.path,
                    query,
                    case_sensitive=self._config.case_sensitive,
                )
            elif isinstance(parser, dbsearcher.search.parsers.CSVParser):
                result_iter = parser.parse(
                    file_info.path,
                    query,
                    case_sensitive=self._config.case_sensitive,
                )
            elif isinstance(parser, dbsearcher.search.parsers.SQLParser):
                result_iter = parser.parse(
                    file_info.path,
                    query,
                    case_sensitive=self._config.case_sensitive,
                )
            else:
                # Fallback for base parser - use text parser behavior
                text_parser: dbsearcher.search.parsers.TextParser = (
                    dbsearcher.search.parsers.TextParser()
                )
                result_iter = text_parser.parse(
                    file_info.path,
                    query,
                    case_sensitive=self._config.case_sensitive,
                )

            for result in result_iter:
                results.append(result)
                # Early termination check
                if len(results) >= self._config.max_results:
                    break

        except dbsearcher.exceptions.DBSearcherError as e:
            self._logger.warning(
                f"Error searching file: {file_info.name}",
                extra={"error": str(e)},
            )
        except Exception as e:
            self._logger.error(
                f"Unexpected error in file: {file_info.name}",
                extra={"error": str(e)},
            )

        return results

    def search(
        self,
        query: str,
    ) -> tuple[dbsearcher.types.SearchResultList, dbsearcher.types.SearchStats]:
        """
        Search all indexed files sequentially.

        Parameters
        ----------
        query
            Search query string.

        Returns
        -------
        tuple[list[SearchResult], SearchStats]
            Search results and statistics.
        """
        if not query or not query.strip():
            raise dbsearcher.exceptions.SearchError(
                "Search query cannot be empty",
                query=query,
            )

        query_normalized: str = query.strip()
        start_time: float = time.perf_counter()

        # Check cache
        if query_normalized in self._result_cache:
            cached: dbsearcher.types.SearchResultList = self._result_cache[
                query_normalized
            ]
            duration: float = time.perf_counter() - start_time
            stats: dbsearcher.types.SearchStats = dbsearcher.types.SearchStats(
                files_searched=self._indexer.get_file_count(),
                total_matches=len(cached),
                duration_seconds=duration,
            )
            self._logger.debug("Cache hit", extra={"query": query_normalized})
            return cached, stats

        files: dbsearcher.types.FileInfoList = self._indexer.get_files()
        all_results: dbsearcher.types.SearchResultList = []

        self._logger.info(
            f"Searching {len(files)} files",
            extra={"query": query_normalized},
        )

        for file_info in files:
            file_results: dbsearcher.types.SearchResultList = self._search_file(
                file_info, query_normalized
            )
            all_results.extend(file_results)

            # Early termination
            if len(all_results) >= self._config.max_results:
                all_results = all_results[: self._config.max_results]
                break

        # Cache results
        self._result_cache[query_normalized] = all_results

        duration = time.perf_counter() - start_time
        stats = dbsearcher.types.SearchStats(
            files_searched=len(files),
            total_matches=len(all_results),
            duration_seconds=duration,
        )

        self._logger.success(
            f"Found {len(all_results)} matches in {duration:.3f}s",
        )

        return all_results, stats

    def search_parallel(
        self,
        query: str,
        *,
        workers: int | None = None,
    ) -> tuple[dbsearcher.types.SearchResultList, dbsearcher.types.SearchStats]:
        """
        Search all indexed files in parallel using ThreadPoolExecutor.

        Parameters
        ----------
        query
            Search query string.
        workers
            Number of parallel workers. Defaults to config value.

        Returns
        -------
        tuple[list[SearchResult], SearchStats]
            Search results and statistics.
        """
        if not query or not query.strip():
            raise dbsearcher.exceptions.SearchError(
                "Search query cannot be empty",
                query=query,
            )

        query_normalized: str = query.strip()
        num_workers: int = workers or self._config.parallel_workers
        start_time: float = time.perf_counter()

        # Check cache
        if query_normalized in self._result_cache:
            cached: dbsearcher.types.SearchResultList = self._result_cache[
                query_normalized
            ]
            duration: float = time.perf_counter() - start_time
            stats: dbsearcher.types.SearchStats = dbsearcher.types.SearchStats(
                files_searched=self._indexer.get_file_count(),
                total_matches=len(cached),
                duration_seconds=duration,
            )
            return cached, stats

        files: dbsearcher.types.FileInfoList = self._indexer.get_files()
        all_results: dbsearcher.types.SearchResultList = []

        self._logger.info(
            f"Parallel search with {num_workers} workers",
            extra={"files": len(files), "query": query_normalized},
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit all file searches
            future_to_file: dict[
                concurrent.futures.Future[dbsearcher.types.SearchResultList],
                dbsearcher.types.FileInfo,
            ] = {
                executor.submit(self._search_file, f, query_normalized): f
                for f in files
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    file_results: dbsearcher.types.SearchResultList = future.result()
                    all_results.extend(file_results)

                    # Early termination check
                    if len(all_results) >= self._config.max_results:
                        # Cancel remaining futures
                        for f in future_to_file:
                            _ = f.cancel()
                        all_results = all_results[: self._config.max_results]
                        break
                except Exception as e:
                    file_info: dbsearcher.types.FileInfo = future_to_file[future]
                    self._logger.warning(
                        f"Failed to search: {file_info.name}",
                        extra={"error": str(e)},
                    )

        # Cache results
        self._result_cache[query_normalized] = all_results

        duration = time.perf_counter() - start_time
        stats = dbsearcher.types.SearchStats(
            files_searched=len(files),
            total_matches=len(all_results),
            duration_seconds=duration,
        )

        self._logger.success(
            f"Parallel: {len(all_results)} matches in {duration:.3f}s",
        )

        return all_results, stats

    def clear_cache(self) -> None:
        """Clear the result cache."""
        self._result_cache.clear()
        self._indexer.invalidate()
        self._logger.debug("Cache cleared")

    def get_file_stats(self) -> tuple[int, int]:
        """
        Get file statistics.

        Returns
        -------
        tuple[int, int]
            File count and total size in bytes.
        """
        return self._indexer.get_file_count(), self._indexer.get_total_size()

    @property
    def config(self) -> dbsearcher.types.SearchConfig:
        """Get search configuration."""
        return self._config


__all__: list[str] = [
    "SearchEngine",
]
