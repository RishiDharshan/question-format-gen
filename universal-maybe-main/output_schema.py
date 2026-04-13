from pydantic import Field, BaseModel

class GeneratorOutput(BaseModel):
    question: str = Field(..., description="The question according to the output format mentioned in the prompt. This generator only generates 1 question. So number every question with '(1). ' strictly. Follow this pattern strictly because our parser depends on this.")

class SubTopicOutput(BaseModel):
    subtopics: list[str] = Field(..., description="A list of highly distinct and specific sub-topics.")

class ConceptOutput(BaseModel):
    concept: str = Field(..., description="The single core concept or sub-topic being tested by this question. Should be a short, specific label (2-6 words) like 'Net Reproduction Rate', 'Stub Questions', 'Arithmetic Mean', 'Consumer Price Index', 'De Facto Enumeration'. Do NOT use generic labels like 'Statistics' or 'Data Collection'.")