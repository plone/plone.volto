from pathlib import Path
from plone.distribution.api import distribution as dist_api
from plone.distribution.core import Distribution

import pytest


class TestRegistration:

    distribution: Distribution = None

    @pytest.fixture(autouse=True)
    def _setup(self, integration, distribution_name) -> Distribution:
        self.distribution = dist_api.get(name=distribution_name)

    def test_distribution_class(self):
        distribution = self.distribution
        assert isinstance(distribution, Distribution)

    @pytest.mark.parametrize(
        "attr,expected",
        [
            ["title", "Plone Site (Volto)"],
            [
                "description",
                "A Plone Site to be used with a Volto frontend",
            ],
        ],
    )
    def test_distribution_name_description(self, attr, expected):
        distribution = self.distribution
        assert isinstance(distribution, Distribution)
        assert getattr(distribution, attr) == expected

    def test_distribution_has_no_handler(self):
        distribution = self.distribution
        assert distribution.handler is None

    def test_distribution_has_post_handler(self):
        distribution = self.distribution
        assert distribution.post_handler is not None

    @pytest.mark.parametrize(
        "profile",
        [
            "plone.app.contenttypes:default",
            "plonetheme.barceloneta:default",
        ],
    )
    def test_distribution_profiles(self, profile):
        distribution = self.distribution
        assert profile in distribution.profiles

    def test_distribution_has_image(self):
        distribution = self.distribution
        assert isinstance(distribution.image, Path)
        assert distribution.image.exists()

    def test_distribution_has_local_directory(self):
        distribution = self.distribution
        assert isinstance(distribution.directory, Path)
        assert distribution.directory.exists()
