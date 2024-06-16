"""
Un processador de plantillas
"""
from jinja2 import (Environment, FileSystemLoader)
from video import Video


class Processor:
    """
    A class responsible for processing various tasks.

    Attributes:
        None

    Methods:
        None
    """

    def __init__(self, template_path: str):
        """
        Initializes the processor with a specified template path.

        Args:
            template_path (str): The path to the directory containing templates

        Returns:
            None
        """
        self._template_path = template_path

    def process(self, video: Video, template: str) -> str:
        """
        Processes a video using a specified template.

        Args:
            video (Video): The video to be processed
            template (str): The name of the template to use

        Returns:
            str: The processed output string

        Raises:
            ValueError: If an invalid template is specifi
        """
        env = Environment(loader=FileSystemLoader(self._template_path))
        template = env.get_template(template)
        return template.render(video=video)
