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
            storagePath: The path in the storage engine to list.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A list of files and folders in the specified path.

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
            storagePath: The path in the storage engine to list.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A list of files and folders with additional details.

        Raises:
            RuntimeError: If the server returns an error.
        """
        pixel = f'Storage("{self.engine_id}")|ListStoragePathDetails(storagePath="{storagePath}");'
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
            True if the sync is successful, False otherwise.

        Raises:
            RuntimeError: If the server returns an error.
        """
        spaceStr = f',space="{space}"' if space is not None else ""
        metadataStr = f",metadata=[{metadata}]" if metadata is not None else ""
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
        insight_id: Optional[str] = None,
    ):
        """Copies files from a storage path to a local path.

        Args:
            storagePath: The source path in the storage engine.
            localPath: The destination path in the local application.
            space: Optional; The space to use (e.g., project ID, "user").
                   If None, the current insight space is used.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            True if the copy is successful, False otherwise.

        Raises:
            RuntimeError: If the server returns an error.
        """
        spaceStr = f',space="{space}"' if space is not None else ""
        pixel = f'Storage("{self.engine_id}")|PullFromStorage(storagePath="{storagePath}",filePath="{localPath}"{spaceStr});'

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
        metadataStr = f",metadata=[{metadata}]" if metadata is not None else ""
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

            def copyToLocal(self, storageFilePath: str, localFolderPath: str) -> any:
                """Copy a specific file from the storage to the local system."""
                return self.storage_engine.copyToLocal(
                    storageFilePath=storageFilePath, localFolderPath=localFolderPath
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
