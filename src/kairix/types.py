from neomodel import StructuredNode, StringProperty


class SourceDocument(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    source_label = StringProperty(index=True, required=True)
    source_type = StringProperty(index=True, required=True)
    content = StringProperty(required=True)
