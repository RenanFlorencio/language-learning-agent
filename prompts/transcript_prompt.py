from langchain_core.prompts import ChatPromptTemplate

PROMPT = """
    You are a helpful assistant that must extract information from videos using their transcripts.
     
    Your task is to use the transcript to extract the following information about the video and extract the 
    the following fields for each video:
    - level_explanation: A brief explanation of how you arrived at the detected language, level, and suitability for students based on the transcript content.
    - detected_language: The language detected in the video content.
    - detected_level: The language proficiency level detected in the video content.
    - for_students: Indicates whether the video is suitable for students.
     
    The detected_language should be the language of the transcript. If you cannot determine the language, you can leave it as None.

    To assess detected_level, use the CEFR scale (A1-C2):
    - A1/A2: Simple vocabulary, short sentences, everyday topics
    - B1/B2: Varied vocabulary, complex sentences, abstract topics
    - C1/C2: Native-like vocabulary, idioms, complex grammatical structures
        
    for_students is True if the video appears designed for language learners:
    - Easy vocabulary
    - Explicit vocabulary explanations
    - No slang or idioms without explanation
    - Teacher/student format
    It is False if the video is native content not designed for learners.
     
    Return the updated list of VideoInfo objects with the three 
    fields filled in for each video where transcript was available.

    Here is the transcript of the video:
    <transcript>
    {transcript}
    </transcript>

    """