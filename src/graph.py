from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_models.writer import ChatWriter
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from pydantic import ValidationError
import json

import configuration
from prompts import (
    blog_planner_instructions,
    main_body_section_writer_instructions,
    intro_conclusion_instructions
)
from state import (
    Sections,
    BlogState,
    BlogStateInput,
    BlogStateOutput,
    SectionState
)
from utils import (
    load_and_format_urls,
    read_dictation_file,
    format_sections
)


load_dotenv()

model = ChatWriter(model='palmyra-creative')

def generate_blog_plan(state: BlogState, config: RunnableConfig):
    """Generate the blog plan"""

    user_instructions = read_dictation_file(state.transcribed_notes_file)

    configurable = configuration.Configuration.from_runnable_config(config)
    blog_structure = configurable.blog_structure

    sections_prompt = blog_planner_instructions.format(user_instructions=user_instructions, blog_structure=blog_structure)

    # Add a structured output prompt to the sections_prompt
    structured_prompt = f"""{sections_prompt}

Please respond with a valid JSON object in the following format:
{{
    "sections": [
        {{
            "name": "Section Name",
            "description": "Brief overview of the main topics and concepts to be covered in this section",
            "content": "",
            "main_body": true or false
        }}
    ]
}}

Ensure the response is valid JSON that can be parsed."""

    # Use the ChatWriter model that's already working in the rest of the code
    response = model.invoke([
        SystemMessage(content="You are an expert Dungeon Master. Generate a structured D&D campaign story outline based on the workflow instructions."),
        HumanMessage(content=structured_prompt)
    ])
    
    # Extract and parse the JSON response
    try:
        # Try to extract JSON from the response content
        response_text = response.content
        
        # Find JSON in the response (it might be wrapped in markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            # Try to find JSON object directly
            json_str = response_text
            
        # Parse the JSON
        parsed_data = json.loads(json_str)
        
        # Convert to Sections object
        report_sections = Sections(**parsed_data)
        
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Failed to parse blog sections from response: {e}\nResponse: {response.content}")
    
    print("\n" + "="*80)
    print("🐉 D&D CAMPAIGN STORY OUTLINE CREATED")
    print("="*80)
    for i, section in enumerate(report_sections.sections, 1):
        print(f"\n{i}. {section.name}")
        print(f"   Story Arc: {section.description}")
        print(f"   Main Chapter: {'⚔️' if section.main_body else '📜'}")
        print("-" * 60)
    print("="*80 + "\n")

    return {"sections": report_sections.sections, "user_instructions": user_instructions}

def write_section(state: SectionState):
    """Write a chapter of the D&D campaign story"""

    section = state.section
    urls = state.urls
    user_instructions = state.user_instructions

    url_source_str = "" if not urls else load_and_format_urls(urls)

    system_instructions = main_body_section_writer_instructions.format(section_name=section.name, 
                                                                       section_topic=section.description, 
                                                                       user_instructions=user_instructions, 
                                                                       source_urls=url_source_str)

    section_content = model.invoke([SystemMessage(content=system_instructions)] + [HumanMessage(content="Write this chapter of the D&D campaign story with vivid descriptions, character details, and engaging narrative.")])
    
    section.content = section_content.content
    
    print(f"⚔️  Chapter written: {section.name}")

    return {"completed_sections": [section]}

def write_final_sections(state: SectionState):
    """Write prologue/epilogue of the D&D campaign story"""

    section = state.section
    
    system_instructions = intro_conclusion_instructions.format(section_name=section.name, 
                                                               section_topic=section.description, 
                                                               main_body_sections=state.blog_main_body_sections, 
                                                               source_urls=state.urls)

    section_content = model.invoke([SystemMessage(content=system_instructions)] + [HumanMessage(content="Craft an epic prologue or epilogue for this D&D campaign story that sets the mood and engages the players.")])
    
    section.content = section_content.content
    
    print(f"📜 Story section complete: {section.name}")

    return {"completed_sections": [section]}

def initiate_section_writing(state: BlogState):
    """Kick off parallel writing of main body sections"""
        
    print(f"\n🎲 Weaving {len([s for s in state.sections if s.main_body])} main story chapters...")
    
    return [
        Send("write_section", SectionState(
            section=s,
            user_instructions=state.user_instructions,
            urls=state.urls,
            completed_sections=[]
        )) 
        for s in state.sections 
        if s.main_body
    ]

def gather_completed_sections(state: BlogState):
    """Gather completed main body sections"""

    completed_sections = state.completed_sections
    if completed_sections is None:
        completed_sections = []
    completed_report_sections = format_sections(completed_sections)
    
    print(f"\n📚 Compiled {len(completed_sections)} main story chapters")

    return {"blog_main_body_sections": completed_report_sections}

def initiate_final_section_writing(state: BlogState):
    """Kick off parallel writing of final sections"""

    final_sections = [s for s in state.sections if not s.main_body]
    print(f"\n✨ Crafting {len(final_sections)} prologue/epilogue sections...")
    
    return [
        Send("write_final_sections", SectionState(
            section=s,
            blog_main_body_sections=state.blog_main_body_sections,
            urls=state.urls,
            completed_sections=[]
        )) 
        for s in state.sections 
        if not s.main_body
    ]

def compile_final_blog(state: BlogState):
    """Compile the final D&D campaign story"""

    sections = state.sections
    completed_sections = {s.name: s.content for s in state.completed_sections}

    for section in sections:
        section.content = completed_sections[section.name]

    all_sections = "\n\n".join([s.content for s in sections])
    
    print(f"\n🏰 Epic D&D campaign story complete with {len(sections)} chapters!")

    return {"final_blog": all_sections}

builder = StateGraph(BlogState, input=BlogStateInput, output=BlogStateOutput, config_schema=configuration.Configuration)
builder.add_node("generate_blog_plan", generate_blog_plan)
builder.add_node("write_section", write_section)
builder.add_node("compile_final_blog", compile_final_blog)
builder.add_node("gather_completed_sections", gather_completed_sections)
builder.add_node("write_final_sections", write_final_sections)
builder.add_edge(START, "generate_blog_plan")
builder.add_conditional_edges("generate_blog_plan", initiate_section_writing, ["write_section"])
builder.add_edge("write_section", "gather_completed_sections")
builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
builder.add_edge("write_final_sections", "compile_final_blog")
builder.add_edge("compile_final_blog", END)

graph = builder.compile() 
