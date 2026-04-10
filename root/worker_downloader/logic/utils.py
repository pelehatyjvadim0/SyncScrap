import hashlib

class DownloaderUtils:
    @staticmethod
    async def get_url_hash(url: str) -> str:
        return hashlib.blake2b(url.encode(), digest_size=8).hexdigest()