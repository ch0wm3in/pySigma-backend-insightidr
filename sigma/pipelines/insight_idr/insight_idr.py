from sigma.processing.conditions import IncludeFieldCondition, MatchStringCondition, LogsourceCondition, RuleProcessingItemAppliedCondition, RuleProcessingCondition
from sigma.processing.pipeline import ProcessingItem, ProcessingPipeline
from sigma.processing.transformations import ChangeLogsourceTransformation, RuleFailureTransformation, DetectionItemFailureTransformation, FieldMappingTransformation
from sigma.pipelines.common import logsource_windows_network_connection,logsource_windows_network_connection_initiated, logsource_windows_process_creation, logsource_windows_dns_query
from sigma.rule import SigmaRule

def logsource_generic_dns_query() -> LogsourceCondition:
    return LogsourceCondition(
        category="dns"
    )

def logsource_web_proxy() -> LogsourceCondition:
    return LogsourceCondition(
        category="proxy"
    )

def logsource_firewall() -> LogsourceCondition:
    return LogsourceCondition(
        category="firewall"
    )

class AggregateRuleProcessingCondition(RuleProcessingCondition):
    """"""
    def match(self, pipeline : "sigma.processing.pipeline.ProcessingPipeline", rule : SigmaRule) -> bool:
        """Match condition on Sigma rule."""
        agg_function_strings = ["| count", "| min", "| max", "| avg", "| sum", "| near"]
        condition_string = " ".join([item.lower() for item in rule.detection.condition])
        if any(f in condition_string for f in agg_function_strings):
            return True
        else:
            return False


def insight_idr_pipeline():
    return ProcessingPipeline(
        name="Generic Log Sources to Rapid7 InsightIDR Transformation",
        priority=10,
        items=[
            # # Process Creation field mapping
            # ProcessingItem(
            #     identifier="insight_idr_process_creation_fieldmapping",
            #     transformation=FieldMappingTransformation({
            #         "ProcessId": "process.pid",
            #         "Image": "process.exe_path",
            #         "FileVersion": "process.exe_file.version",
            #         "Description": "process.exe_file.description",
            #         "Product": "process.exe_file.product_name",
            #         "Company": "process.exe_file.author",
            #         "OriginalFileName": "process.name",
            #         "CommandLine": "process.cmd_line",
            #         "User": "process.username",
            #         "ParentProcessId": "parent_process.pid",
            #         "ParentImage": "parent_process.exe_path",
            #         "ParentCommandLine": "parent_process.cmd_line",
            #         "ParentUser": "parent_process.username",
            #         "md5": "process.exe_file.hashes.md5",
            #         "sha1": "process.exe_file.hashes.sha1",
            #         "sha256": "process.exe_file.hashes.sha256"
            #     }),
            #     rule_conditions=[
            #         logsource_windows_process_creation(),
            #     ]
            # ),
            # # Handle unsupported Process Start fields
            # ProcessingItem(
            #     identifier="insight_idr_fail_process_start_fields",
            #     transformation=DetectionItemFailureTransformation("The InsightIDR backend does not support the CurrentDirectory, IntegrityLevel, or imphash fields for process start rules."),
            #     rule_conditions=[
            #         logsource_windows_process_creation()
            #     ],
            #     field_name_conditions=[
            #         IncludeFieldCondition(
            #             fields=[
            #                 "CurrentDirectory",
            #                 "IntegrityLevel",
            #                 "imphash",
            #                 "Imphash",
            #                 "LogonId"
            #             ]
            #         )
            #     ]
            # ),
            # # Change logsource properties
            # ProcessingItem(
            #     identifier="insight_idr_process_start_logsource",
            #     transformation=ChangeLogsourceTransformation(
            #         category="process_start_event",
            #         product="windows"
            #     ),
            #     rule_conditions=[
            #         logsource_windows_process_creation(),
            #     ]
            # ),

            # # DNS Request field mapping
            # ProcessingItem(
            #     identifier="insight_idr_dns_query_fieldmapping",
            #     rule_condition_linking=any,
            #     transformation=FieldMappingTransformation({
            #         "QueryName": "query",
            #         "Computer": "asset",
            #         "record_type": "query_type"
            #     }),
            #     rule_conditions=[
            #         logsource_windows_dns_query(),
            #         logsource_generic_dns_query()
            #     ]
            # ),
            # # Handle unsupported DNS query fields
            # ProcessingItem(
            #     identifier="insight_idr_fail_dns_fields",
            #     rule_condition_linking=any,
            #     transformation=DetectionItemFailureTransformation("The InsightIDR backend does not support the ProcessID, QueryStatus, QueryResults, Image, or answer fields for DNS events."),
            #     rule_conditions=[
            #         logsource_windows_dns_query(),
            #         logsource_generic_dns_query()
            #     ],
            #     field_name_conditions=[
            #         IncludeFieldCondition(
            #             fields=[
            #                 "ProcessId",
            #                 "QueryStatus",
            #                 "QueryResults",
            #                 "Image",
            #                 "answer"
            #             ]
            #         )
            #     ]
            # ),
            # # Change log source properties
            # ProcessingItem(
            #     identifier="insight_idr_dns_query_logsource",
            #     rule_condition_linking=any,
            #     transformation=ChangeLogsourceTransformation(
            #         category="dns"
            #     ),
            #     rule_conditions=[
            #         logsource_windows_dns_query(),
            #         logsource_generic_dns_query()
            #     ]
            # ),

            # Web Proxy field mapping
            ProcessingItem(
                identifier="insight_idr_web_proxy_fieldmapping",
                transformation=FieldMappingTransformation({
                    "c-uri": "url",
                    "c-uri-query": "url_path",
                    "cs-bytes": "incoming_bytes",
                    "cs-host": "url_host",
                    "cs-method": "http_method",
                    "r-dns": "url_host",
                    "sc-bytes": "outgoing_bytes",
                    "src_ip": "source_ip",
                    "dst_ip": "destination_ip"
                }),
                rule_conditions=[
                    logsource_web_proxy(),
                ]
            ),
            # Handle unsupported Web Proxy event fields
            ProcessingItem(
                identifier="insight_idr_fail_web_proxy_fields",
                rule_condition_linking=all,
                transformation=DetectionItemFailureTransformation("The InsightIDR backend does not support the c-uri-extension, c-uri-stem, c-useragent, cs-cookie, cs-referrer, cs-version, or sc-status fields for web proxy events."),
                rule_conditions=[
                    logsource_web_proxy()
                ],
                field_name_conditions=[
                    IncludeFieldCondition(
                        fields=[
                            "c-uri-extension",
                            "c-uri-stem",
                            "c-useragent",
                            "cs-referrer",
                            "cs-version",
                            "sc-status"
                        ]
                    )
                ]
            ),
            # Change logsource property
            ProcessingItem(
                identifier="insight_idr_web_proxy_logsource",
                transformation=ChangeLogsourceTransformation(
                    category="web_proxy"
                ),
                rule_conditions=[
                    logsource_web_proxy(),
                ]
            ),
            # Firewall - this is a placeholder. Firewall rules not yet supported :(
            ProcessingItem(
                identifier="insight_idr_firewall_fieldmapping",
                transformation=FieldMappingTransformation({
                    "src_ip": "source_address",
                    "src_port": "source_port",
                    "dst_ip": "destination_address",
                    "dst_port": "destination_port",
                    "username": "user"
                }),
                rule_conditions=[
                    logsource_firewall(),
                ]
            ),

            # Handle unsupported log sources - here we are checking whether none of the log source-specific transformations
            # that were set above have applied and throwing a RuleFailureTransformation error if this condition is met. Otherwise,
            # a separate processing item would be needed for every unsupported log source type
            ProcessingItem(
                identifier="insight_idr_fail_rule_not_supported",
                rule_condition_linking=any,
                transformation=RuleFailureTransformation("Rule type not yet supported by the InsightIDR Sigma backend!"),
                rule_condition_negation=True,
                rule_conditions=[
                    RuleProcessingItemAppliedCondition("insight_idr_web_proxy_logsource")
                ],
            ),

            # Handle rules that use aggregate functions
            ProcessingItem(
                identifier="insight_idr_fail_rule_conditions_not_supported",
                transformation=RuleFailureTransformation("Rules with aggregate function conditions like count, min, max, avg, sum, and near are not supported by the InsightIDR Sigma backend!"),
                rule_conditions=[
                    AggregateRuleProcessingCondition()
                ],
            )
        ]
    )
