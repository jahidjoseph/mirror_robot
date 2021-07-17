class DirectDownloadLinkException(Exception):
    """No Method Found For Extracting Direct Download Link From The HTTP Link!"""
    pass


class NotSupportedExtractionArchive(Exception):
    """The Archive Format Use Is Trying To Extract Is Not Supported!"""
    pass
