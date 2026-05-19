"""Protobuf parsing via grpc_tools.protoc."""

from pickled_schema.proto.parser import parse_proto_file

__all__ = ["parse_proto_file"]
