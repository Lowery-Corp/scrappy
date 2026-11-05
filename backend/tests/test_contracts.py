import unittest
import uuid

from pydantic import ValidationError

from repositories.minio import _normalize_path
from repositories.user_conversation import _conversation_name_from_message
from schemas.user_conversation import UserConversationUpdate


class ContractTests(unittest.TestCase):
    def test_conversation_name_is_normalized_and_bounded(self) -> None:
        self.assertEqual(_conversation_name_from_message("  hello\n world "), "hello world")
        self.assertEqual(_conversation_name_from_message("   "), "New Conversation")
        self.assertLessEqual(len(_conversation_name_from_message("x" * 200)), 63)

    def test_storage_paths_reject_traversal(self) -> None:
        self.assertEqual(_normalize_path("/home/docs/report.txt"), "home/docs/report.txt")
        with self.assertRaises(ValueError):
            _normalize_path("home/../secrets.txt")

    def test_conversation_update_accepts_api_file_ids_alias(self) -> None:
        file_id = uuid.uuid4()
        update = UserConversationUpdate.model_validate({"file_ids": [str(file_id)]})
        self.assertEqual(update.relevant_file_ids, [file_id])

    def test_conversation_update_rejects_invalid_file_id(self) -> None:
        with self.assertRaises(ValidationError):
            UserConversationUpdate.model_validate({"file_ids": ["not-a-uuid"]})


if __name__ == "__main__":
    unittest.main()
