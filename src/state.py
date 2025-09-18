import operator
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from typing_extensions import Annotated, List

class Section(BaseModel):
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )
    content: str = Field(
        description="The content of the section."
    )   
    main_body: bool = Field(
        description="Whether this is a main body section."
    )   

class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the report.",
    )

@dataclass(kw_only=True)
class BlogState:
    transcribed_notes_file: str   
    urls: List[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list) 
    completed_sections: Annotated[list, operator.add]
    blog_main_body_sections: str | None = field(default=None)
    final_blog: str | None = field(default=None)
    user_instructions: str | None = field(default=None)
    
@dataclass(kw_only=True)
class BlogStateInput:
    transcribed_notes_file: str
    urls: List[str] = field(default_factory=list)

@dataclass(kw_only=True)
class BlogStateOutput:
    final_blog: str | None = field(default=None)

@dataclass(kw_only=True)
class SectionState:
    section: Section
    user_instructions: str | None = field(default=None)
    urls: List[str] = field(default_factory=list)
    blog_main_body_sections: str | None = field(default=None)
    completed_sections: list[Section] = field(default_factory=list)
    
@dataclass(kw_only=True)
class SectionOutputState:
    completed_sections: list[Section] = field(default_factory=list)