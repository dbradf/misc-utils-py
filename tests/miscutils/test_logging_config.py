import logging

import miscutils.logging_config as under_test
import structlog
from miscutils.testing import relative_patch_maker

patch = relative_patch_maker(under_test.__name__)


class TestVerbosity:
    def test_logging_warning(self):
        assert under_test.Verbosity.WARNING.level() == logging.WARNING

    def test_logging_info(self):
        assert under_test.Verbosity.INFO.level() == logging.INFO

    def test_logging_debug(self):
        assert under_test.Verbosity.DEBUG.level() == logging.DEBUG

    def test_logging_max(self):
        assert under_test.Verbosity.MAX.level() == logging.DEBUG


class TestDefaultConfiguration:
    @patch("structlog.processors.UnicodeDecoder")
    @patch("structlog.processors.StackInfoRenderer")
    @patch("structlog.stdlib.PositionalArgumentsFormatter")
    @patch("structlog.stdlib.LoggerFactory")
    @patch("sys.stdout")
    @patch("structlog.configure")
    @patch("logging.basicConfig")
    def test_text_logging(
        self,
        mock_basic_config,
        mock_configure,
        mock_stdout,
        mock_logger_factory,
        mock_formatter,
        mock_renderer,
        mock_decoder,
    ):
        under_test.default_logging(
            under_test.Verbosity.WARNING, log_format=under_test.LogFormat.TEXT
        )
        expected_format = "[%(levelname)s %(filename)s:%(funcName)s:%(lineno)s] %(message)s"
        mock_basic_config.assert_called_with(level=30, stream=mock_stdout, format=expected_format)
        mock_configure.assert_called_with(
            logger_factory=mock_logger_factory.return_value,
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            processors=[
                structlog.stdlib.filter_by_level,
                mock_formatter.return_value,
                mock_renderer.return_value,
                structlog.processors.format_exc_info,
                mock_decoder.return_value,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
        )

    @patch("structlog.threadlocal.wrap_dict")
    @patch("structlog.processors.UnicodeDecoder")
    @patch("structlog.processors.StackInfoRenderer")
    @patch("structlog.stdlib.PositionalArgumentsFormatter")
    @patch("structlog.stdlib.LoggerFactory")
    @patch("structlog.configure")
    @patch("logging.config.dictConfig")
    def test_json_logging(
        self,
        mock_dict_config,
        mock_configure,
        mock_logger_factory,
        mock_formatter,
        mock_renderer,
        mock_decoder,
        mock_wrapper,
    ):
        under_test.default_logging(
            under_test.Verbosity.WARNING, log_format=under_test.LogFormat.JSON
        )
        mock_dict_config.assert_called_with(
            {
                "version": 1,
                "formatters": {
                    "json": {
                        "format": "%(message)s $(lineno)d $(filename)s",
                        "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    }
                },
                "handlers": {"json": {"class": "logging.StreamHandler", "formatter": "json"}},
                "loggers": {"": {"handlers": ["json"], "level": 30}},
            }
        )
        mock_configure.assert_called_with(
            context_class=mock_wrapper.return_value,
            logger_factory=mock_logger_factory.return_value,
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                mock_formatter.return_value,
                mock_renderer.return_value,
                structlog.processors.format_exc_info,
                mock_decoder.return_value,
                structlog.stdlib.render_to_log_kwargs,
            ],
        )

    @patch("logging.getLogger")
    def test_external_logs(self, mock_get_logger):
        under_test.default_logging(
            under_test.Verbosity.DEBUG,
            under_test.LogFormat.JSON,
            external_logs=["some_external_log"],
        )
        mock_get_logger.assert_called_with("some_external_log")
        mock_get_logger.return_value.setLevel.assert_called_with(logging.WARNING)
