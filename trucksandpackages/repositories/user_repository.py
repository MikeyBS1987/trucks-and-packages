from trucksandpackages.repositories.abstract_repository import AbstractRepository

from typing import List

from google.cloud import datastore
from trucksandpackages.domain import model
from trucksandpackages.repositories.abstract_repository import AbstractRepository

class UserRepository(AbstractRepository):

    def __init__(
        self,
        client_session: datastore.Client,
        datastore_config: datastore,
        transaction: datastore.Transaction
    ):
        self._client_session = client_session
        self._datastore = datastore_config
        self._transaction = transaction
        self._added_entity: datastore.Entity = None
        self._id_of_deleted_entity: str = None

    @property
    def id_of_added_entity(self) -> str:
        return self._added_entity.key.id

    @property
    def id_of_deleted_entity(self) -> str:
        return self._id_of_deleted_entity

    def add(self, user: model.User):
        if user.user_id:
            key = self._client_session.key("users", int(user.user_id))
        else:
            key = self._client_session.key("users")

        entity = self._datastore.Entity(key=key)
        entity.update({
            "auth_id": user.auth_id,
            "trucks": []
        })
        if user.has_assigned_trucks():
            for truck_id in user.truck_ids:
                entity["trucks"].append(truck_id)
        
        self._transaction.put(entity)
        self._added_entity = entity


    def get(self, user_id: str):
        key = self._client_session.key("users", int(user_id))
        result = self._client_session.get(key=key)
        if result:
            user = model.User(
                user_id=result.key.id
            )
            for truck_id in result["trucks"]:
                user.assign_truck(truck_id)
            return user
        else:
            return None

    def get_list(self) -> List[model.User]:
        query = self._client_session.query(kind="users")
        results = query.fetch()
        users = []
        for item in results:
            user = model.User(
                auth_id=item["auth_id"],
                user_id=item.key.id
            )
            for truck_id in item["trucks"]:
                user.assign_truck(truck_id)
            users.append(user)
        return users

    def remove(self):
        pass