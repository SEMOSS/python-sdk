from typing import Optional, Dict
import logging
from ai_server.server_resources.server_proxy import ServerProxy

logger: logging.Logger = logging.getLogger(__name__)


class StorageEngine(ServerProxy):
    def __init__(self, engine_id: str, insight_id: Optional[str] = None):
        super().__init__()

        self.engine_id = engine_id
        self.insight_id = insight_id

        logger.info(f"StorageEngine initialized with engine id {engine_id}")

    def __execute_pixel(self, pixel: str, insight_id: Optional[str] = None):
        if insight_id is None:
            insight_id = self.insight_id

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def list(self, storagePath: str, insight_id: Optional[str] = None):
        """Lists the files and folders in a given storage path.

        Args:
            storagePath: The path in the storage engine to list. Use "/" for the root.
                         On Azure the root lists the containers in the account, and
                         every path below it starts with a container name, for example
                         "mycontainer/myfolder".
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A list of names in the specified path. Folders come back with a trailing
            slash, files without one.

        Raises:
            RuntimeError: If the server returns an error.
        """
        pixel = (
            f'Storage("{self.engine_id}")|ListStoragePath(storagePath="{storagePath}");'
        )
        return self.__execute_pixel(pixel, insight_id)

    def listDetails(self, storagePath: str, insight_id: Optional[str] = None):
        """Lists the files and folders in a given storage path with additional details.

        Args:
            storagePath: The path in the storage engine to list. Use "/" for the root.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A list of dicts, one per entry, each with the keys "Path", "Name", "Size",
            "MimeType", "ModTime", "IsDir" and "Metadata". "Path" is absolute within
            the engine, so it can be handed straight back to any other method here.

        Raises:
            RuntimeError: If the server returns an error.
        """
        pixel = f'Storage("{self.engine_id}")|ListStoragePathDetails(storagePath="{storagePath}");'
        return self.__execute_pixel(pixel, insight_id)

    def listVersions(self, storagePath: str, insight_id: Optional[str] = None):
        """Lists the stored versions of a single file.

        Only meaningful on engines that keep versions, which today means S3 style
        engines with bucket versioning turned on.

        Args:
            storagePath: The path of the file in the storage engine. This has to name
                         a file, not a folder.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A list of dicts, newest first, each with "versionId", "lastModified",
            "size", "isLatest" and "key". A "versionId" from here can be passed to
            copyToLocal to pull that specific version.

        Raises:
            RuntimeError: If the server returns an error, including when the engine
                          does not support versioning.
        """
        pixel = f'Storage("{self.engine_id}")|ListStorageVersions(storagePath="{storagePath}");'
        return self.__execute_pixel(pixel, insight_id)

    def syncLocalToStorage(
        self,
        storagePath: str,
        localPath: str,
        space: Optional[str] = None,
        metadata: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ):
        """Syncs files from a local path to a storage path.

        Args:
            storagePath: The destination path in the storage engine.
            localPath: The source path in the local application.
            space: Optional; The space to use (e.g., project ID, "user").
                   If None, the current insight space is used.
            metadata: Optional; A dictionary of metadata to associate with the files.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A dict describing the outcome of the sync:

                {
                    "storagePath": "your/storage/path",
                    "status": "SUCCESS",
                    "uploadedFiles": ["your/storage/path/a.csv"],
                    "skippedFiles": ["your/storage/path/b.csv"],
                    "failedFiles": [],
                }

            "status" is "SUCCESS" when nothing failed, "PARTIAL" when some files made
            it and others did not, and "FAILED" when none did. A partial sync does not
            raise, so check the status to know that every file arrived.
            "skippedFiles" were already in storage and unchanged, so they were not
            rewritten.

            Engines that hand the whole transfer off in a single call cannot name
            individual files and report "SUCCESS" with empty lists, so an empty
            "uploadedFiles" means "not reported", not "nothing uploaded".

        Raises:
            RuntimeError: If the server returns an error.
        """
        spaceStr = f',space="{space}"' if space is not None else ""
        metadataStr = f",metadata=[{metadata}]" if metadata else ""
        pixel = f'Storage("{self.engine_id}")|SyncLocalToStorage(storagePath="{storagePath}",filePath="{localPath}"{spaceStr}{metadataStr});'

        return self.__execute_pixel(pixel, insight_id)

    def syncStorageToLocal(
        self,
        storagePath: str,
        localPath: str,
        space: Optional[str] = None,
        insight_id: Optional[str] = None,
    ):
        """Syncs files from a storage path to a local path.

        Args:
            storagePath: The source path in the storage engine.
            localPath: The destination path in the local application.
            space: Optional; The space to use (e.g., project ID, "user").
                   If None, the current insight space is used.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            True if the sync is successful, False otherwise.

        Raises:
            RuntimeError: If the server returns an error.
        """
        spaceStr = f',space="{space}"' if space is not None else ""
        pixel = f'Storage("{self.engine_id}")|SyncStorageToLocal(storagePath="{storagePath}",filePath="{localPath}"{spaceStr});'

        return self.__execute_pixel(pixel, insight_id)

    def copyToLocal(
        self,
        storagePath: str,
        localPath: str,
        space: Optional[str] = None,
        version: Optional[str] = None,
        insight_id: Optional[str] = None,
    ):
        """Copies files from a storage path to a local path.

        Args:
            storagePath: The source path in the storage engine.
            localPath: The destination path in the local application.
            space: Optional; The space to use (e.g., project ID, "user").
                   If None, the current insight space is used.
            version: Optional; A version id from listVersions, to pull that version
                     instead of the current one. Only engines that keep versions
                     accept this.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            True if the copy is successful, False otherwise.

        Raises:
            RuntimeError: If the server returns an error.
        """
        spaceStr = f',space="{space}"' if space is not None else ""
        versionStr = f',version="{version}"' if version else ""
        pixel = f'Storage("{self.engine_id}")|PullFromStorage(storagePath="{storagePath}",filePath="{localPath}"{spaceStr}{versionStr});'

        return self.__execute_pixel(pixel, insight_id)

    def copyToStorage(
        self,
        storagePath: str,
        localPath: str,
        space: Optional[str] = None,
        metadata: Optional[Dict] = {},
        insight_id: Optional[str] = None,
    ):
        """Copies files from a local path to a storage path.

        Args:
            storagePath: The destination path in the storage engine.
            localPath: The source path in the local application.
            space: Optional; The space to use (e.g., project ID, "user").
                   If None, the current insight space is used.
            metadata: Optional; A dictionary of metadata to associate with the files.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            True if the copy is successful, False otherwise.

        Raises:
            RuntimeError: If the server returns an error.
        """
        spaceStr = f',space="{space}"' if space is not None else ""
        metadataStr = f",metadata=[{metadata}]" if metadata else ""
        pixel = f'Storage("{self.engine_id}")|PushToStorage(storagePath="{storagePath}",filePath="{localPath}"{spaceStr}{metadataStr});'

        return self.__execute_pixel(pixel, insight_id)

    def deleteFromStorage(
        self,
        storagePath: str,
        leaveFolderStructure: Optional[bool] = False,
        insight_id: Optional[str] = None,
    ):
        """Deletes files from a storage path.

        Args:
            storagePath: The path in the storage engine to delete.
            leaveFolderStructure: Optional; If True, the folder structure is maintained after deletion.
                                Defaults to False.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            True if the deletion is successful, False otherwise.

        Raises:
            RuntimeError: If the server returns an error.
        """
        leaveFolderStructureStr = "true" if leaveFolderStructure else "false"
        pixel = f'Storage("{self.engine_id}")|DeleteFromStorage(storagePath="{storagePath}",leaveFolderStructure={leaveFolderStructureStr});'

        return self.__execute_pixel(pixel, insight_id)

    def updateFileMetadata(
        self,
        storagePath: str,
        metadata: Dict,
        insight_id: Optional[str] = None,
    ):
        """Replaces the metadata on a file already in storage.

        This rewrites the metadata rather than merging into it, so pass every key the
        file should end up with. SMB/CIFS and SFTP have nowhere to keep user metadata
        and ignore it.

        Args:
            storagePath: The path of the file in the storage engine.
            metadata: A dictionary of metadata to set on the file. Values are stored
                      as strings.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            True if the update is successful.

        Raises:
            RuntimeError: If the server returns an error.
        """
        pixel = f'Storage("{self.engine_id}")|UpdateStorageFileMetadata(storagePath="{storagePath}",metadata=[{metadata}]);'

        return self.__execute_pixel(pixel, insight_id)

    def getFileAsBase64(
        self,
        storagePath: str,
        convertToPdf: Optional[bool] = False,
        insight_id: Optional[str] = None,
    ):
        """Reads a single file out of storage as a base64 string.

        Useful for handing a file to something that wants its bytes without writing it
        to the insight workspace first.

        Args:
            storagePath: The path of the file in the storage engine.
            convertToPdf: Optional; If True, convert the file to a PDF before encoding
                          it. Defaults to False.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            The file contents as a base64 encoded string.

        Raises:
            RuntimeError: If the server returns an error.
        """
        convertToPdfStr = ",convertToPdf=true" if convertToPdf else ""
        pixel = f'Storage("{self.engine_id}")|GetStorageFileAsBase64(storagePath="{storagePath}"{convertToPdfStr});'

        return self.__execute_pixel(pixel, insight_id)

    def to_langchain_storage(self):
        """Transform the storage engine into a langchain BaseStore object so that it can be used with langchain code"""
        from langchain_core.stores import BaseStore

        class SemossLangchainStorage(BaseStore):
            engine_id: str
            storage_engine: StorageEngine
            insight_id: Optional[str]

            def __init__(self, storage_engine: StorageEngine):
                """Initialize with the provided storage engine."""
                self.engine_id = storage_engine.engine_id
                self.storage_engine = storage_engine

            def list(self, storagePath: str) -> any:
                """Retrieve the file list from storage."""
                return self.storage_engine.list(storagePath=storagePath)

            def listDetails(self, storagePath: str) -> any:
                """Retrieve the files details list from storage."""
                return self.storage_engine.listDetails(storagePath=storagePath)

            def syncLocalToStorage(self, localPath: str, storagePath: str) -> any:
                """Sync the files from local to storage."""
                return self.storage_engine.syncLocalToStorage(
                    localPath=localPath, storagePath=storagePath
                )

            def syncStorageToLocal(self, localPath: str, storagePath: str) -> any:
                """Sync the files from storage to local."""
                return self.storage_engine.syncStorageToLocal(
                    localPath=localPath, storagePath=storagePath
                )

            def copyToLocal(self, storagePath: str, localPath: str) -> any:
                """Copy a specific file from the storage to the local system."""
                return self.storage_engine.copyToLocal(
                    storagePath=storagePath, localPath=localPath
                )

            def deleteFromStorage(self, storagePath: str) -> any:
                """Delete a file from storage."""
                return self.storage_engine.deleteFromStorage(storagePath=storagePath)

            def mdelete(self):
                pass

            def mget(self):
                pass

            def mset(self):
                pass

            def yield_keys(self):
                pass

        return SemossLangchainStorage(storage_engine=self)
