import kindly


# The real reason for having this test is so that pytest will find something in an
# otherwise empty project.
def test_version_is_string():
    # As opposed to some more structured type
    assert isinstance(kindly.__version__, str)
