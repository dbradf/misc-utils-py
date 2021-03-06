from unittest.mock import MagicMock

import servicetools.timer as under_test


class TestTimer:
    def test_timing_written_to_log(self):
        logger = MagicMock()

        @under_test.timer(logger, details=True)
        def sample_fn():
            return True

        assert sample_fn()

        logger.log.assert_called_once()
