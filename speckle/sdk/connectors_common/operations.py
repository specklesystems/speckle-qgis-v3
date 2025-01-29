from dataclasses import dataclass
from typing import Any, Dict, List

from speckle.host_apps.qgis.connectors.utils import QgisThreadContext
from speckle.sdk.connectors_common.api import IClientFactory, IOperations
from speckle.sdk.connectors_common.builders import (
    IRootObjectBuilder,
    RootObjectBuilderResult,
)
from speckle.sdk.connectors_common.credentials import IAccountManager
from speckle.ui.models import SendInfo
from specklepy.core.api import operations
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.inputs.version_inputs import CreateVersionInput
from specklepy.objects.base import Base
from specklepy.transports.server.server import ServerTransport


class AccountService:
    account_manager: IAccountManager

    def __init__(self, account_manager: IAccountManager):
        self.account_manager = account_manager

    def get_account_with_server_url_fallback(self, account_id: str, server_url: str):
        try:
            return self.account_manager.get_account(account_id)
        except:
            # TODO define exception type
            accounts: List[Account] = self.account_manager.get_accounts(server_url)

            try:
                return accounts[0]
            except IndexError:
                # TODO define exception type
                raise Exception(
                    message=f"No any account found that matches with server {server_url}"
                )


@dataclass
class SendOperationResult:
    root_obj_id: str
    converted_references: Dict[str, str]  # ["Id", "ObjectReference"]


class SendOperation:
    root_object_builder: IRootObjectBuilder
    send_conversion_cache: "ISendConversionCache"
    account_service: AccountService
    send_progress: "ISendProgress"
    operations: IOperations
    client_factory: IClientFactory
    activity_factory: "IActivityFactory"

    def __init__(
        self,
        root_object_builder: IRootObjectBuilder,
        send_conversion_cache: "ISendConversionCache",
        account_service: AccountService,
        send_progress: "ISendProgress",
        operations: IOperations,
        client_factory: IClientFactory,
        activity_factory: "IActivityFactory",
    ):
        self.root_object_builder = root_object_builder
        self.send_conversion_cache = send_conversion_cache
        self.account_service = account_service
        self.send_progress = send_progress
        self.operations = operations
        self.client_factory = client_factory
        self.activity_factory = activity_factory

    def execute(
        self,
        objects: List[Any],
        send_info: SendInfo,
        on_operation_progressed: "IProgress[CardProgress]",
        ct: "CancellationToken",
    ) -> SendOperationResult:

        build_result: RootObjectBuilderResult = self.root_object_builder.build(
            objects, send_info, on_operation_progressed, ct
        )
        build_result.root_object["version"] = 3

        obj_id_and_converted_refs = self.send(
            build_result.root_object, send_info, on_operation_progressed, ct
        )

        return SendOperationResult(
            obj_id_and_converted_refs[0],
            build_result.conversion_results,
        )

    def send(
        self,
        commit_object: Base,
        send_info: SendInfo,
        on_operation_progressed: "IProgress[CardProgress]" = None,
        ct: "CancellationToken" = None,
    ):
        # TODO
        # ct.ThrowIfCancellationRequested()
        # on_operation_progressed.report(CardProgress(status="Uploading...",progress=None))

        account: Account = self.account_service.get_account_with_server_url_fallback(
            account_id=send_info.account_id, server_url=send_info.server_url
        )
        r"""
        obj_id_and_converted_refs = self.operations.send(
            send_info.server_url,
            send_info.project_id,
            account.token,
            commit_object,
            on_operation_progressed,
            ct,
        )
        """
        transport = ServerTransport(
            client=self.client_factory.create(account=account),
            account=account,
            stream_id=send_info.project_id,
        )
        obj_id = operations.send(base=commit_object, transports=[transport])
        # store cache
        # ct.ThrowIfCancellationRequested()
        # on_operation_progressed.report(CardProgress(status="Linking version to model...",progress=None))

        # create a version in the project
        api_client: SpeckleClient = self.client_factory.create(account)

        _ = api_client.version.create(
            CreateVersionInput(
                objectId=obj_id,
                modelId=send_info.model_id,
                projectId=send_info.project_id,
                message="Sent from QGIS v3",
                sourceApplication=send_info.host_application,
            )
        )

        return (obj_id, {})


@dataclass
class ProxyKeys:

    COLOR = "colorProxies"
    RENDER_MATERIAL = "renderMaterialProxies"
    INSTANCE_DEFINITION = "instanceDefinitionProxies"
    GROUP = "groupProxies"
    PARAMETER_DEFINITIONS = "parameterDefinitions"
    PROPERTYSET_DEFINITIONS = "propertySetDefinitions"
