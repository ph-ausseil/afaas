from logging import Logger
import uuid
from autogpt.core.configuration import SystemConfiguration, UserConfigurable
from autogpt.core.planning.base import BasePromptStrategy
from autogpt.core.planning.schema import (
    LanguageModelClassification,
    LanguageModelPrompt,
)
from autogpt.core.planning.utils import json_loads, to_numbered_list
from autogpt.core.resource.model_providers import (
    LanguageModelFunction,
    LanguageModelMessage,
    MessageRole,
)


class RefineUserContextConfiguration(SystemConfiguration):
    model_classification: LanguageModelClassification = UserConfigurable()

class RefineUserContext(BasePromptStrategy):
    STRATEGY_NAME = "refine_user_context"
    CONTEXT_MIN_TOKENS=250,
    CONTEXT_MAX_TOKENS=300

    SYSTEM_PROMPT_INIT = (
"### Instruction :\n\n"
#"You are an AI tasked with assisting a user in formulating their requirements to achieve its goal .\n\n"
# "You are an AI tasked with assisting a user in formulating their requirements.\n\n"
# "To achieve effective assistance, it is essential that the goal provided by the user adheres to the following principles (**COCE Framework**):\n\n"
"To achieve effective assistance, it is essential that the requirements provided by the user adheres to the following principles (**COCE Framework**):\n\n"
" - **Comprehensible**: Your AI needs to be able to understand the goal, even within its limited context window. Minimize ambiguity, and use specific terminologies or semantics that the AI can comprehend.\n"
" - **Outcome-driven**: Focus on the end results or macro-goals that the AI should achieve, rather than measurable micro-goals or the steps that need to be taken to get there.\n"
" - **Context-aware**: The goal should be aware of and clearly define the context in which the AI is expected to function. This is especially important if the AI has a limited understanding of the world or the domain in which it operates.\n"
" - **Explicitness**: The goal must explicitly state what the AI needs to do. There should be no hidden assumptions or implied requirements. Everything that the AI needs to know to complete the goal should be explicitly stated.\n\n"
"Your primary role is to assist the user in adhering to these principles and guide them through the process of formulating requirements that meet these criteria. Please use your capabilities to ensure that the user's goal aligns with these principles by generating questions that guide him closer to our expectations in term of user requirement expression. \n\n"
"### Example:\n\n"
"Imagine a user approaches you with the following request: \"I want to plan a vacation.\" Your task is to assist the user in specifying their vacation plans while adhering to the principles of comprehensibility, outcome-driven focus, context-awareness, and explicitness as outlined above.\n"
"Feel free to adapt this framework to suit the specific needs of your project and provide additional guidance as necessary.\n\n")

    NEW_SYSTEM_PROMPT = ("###  User's Requirements:\n"
#"So far the user have expressed this requirements :\n"
"\"{user_response}\"\n\n"
)
    NEW_ASSISTANT_PROMPT = "How can I help you ?\n"
    NEW_USER_PROMPT = "These are my requirement : {user_response}\n"


    REFINED_ONCE_SYSTEM_PROMPT = ("### User's Journey:\n"
#"So far the user have expressed these requirements :\n"
"\"{user_response}\"\n\n"
"- **Your questions**:\n" 
"{last_questions}\n"
"- **User's Response**: \n"
"{user_response}\n\n"
)

    REFINED_SYSTEM_PROMPT = ("### User's Journey:\n"
#"So far the user have expressed these requirements :\n"
"'{user_last_goal}'\n\n"
"- **Your full history of Questions**:\n" 
"'{questions_history_full}\n"
"- **Your Last Questions**:\n" 
"{last_questions}\n"
"- **User's Last Response**:\n"
"{user_response}\n\n"
)
    #     REFINED_SYSTEM_PROMPT = ("### User's Journey:\n"
    # "So far the user have expressed these requirements :\n"
    # "'{user_last_goal}'\n")
    # REFINED_ASSISTANT_PROMPT = "{last_questions}"
    # REFINED_USER_PROMPT = "{user_response}"

    SYSTEM_PROMPT_FOOTER = ("Guide the user closer to a refined goal by referencing the above journey and adhering to the **COCE Framework**. Provide actionable insights and questions.\n\n"    
"### Note:\n"
"This is an iterative process. Your generated `reformulated_goal` will serve as the user's next goal and the questions will gather further details from the user.\n"
)
    
    SYSTEM_PROMPT_NOTICE = "**IMPORTANT** : YOU MUST USE FUNCTIONS AT YOUR DISPOSAL"
    



    FUNCTION_REFINE_USER_CONTEXT  = {
            "name": "refine_goal",
            "description": "Assists users in refining their requirements using the COCE Framework",
            "parameters": {
                "type": "object",
                "properties": {
                    "reformulated_goal": {
                        "type": "string",
                        "description": f"Reformulated user's requirements expressed in {CONTEXT_MIN_TOKENS} to {CONTEXT_MAX_TOKENS} words, formatted preferably using Markdown. This version **WARNING** It **must** stay true to the user's intent and user requirements."
                        # f"A reformulated version of the user's requirements that should follow the COCE Framework if possible.  This should be between {CONTEXT_MIN_TOKENS} and {CONTEXT_MAX_TOKENS} words, formatted preferably using Markdown."
                    },
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of one to five questions designed extract more detailed and explicit information from the user."
                    }
                },
                "required": ["reformulated_goal", "questions"]
            },
        }
    

    FUNCTION_VALIDATE_GOAL = {
        "name": "validate_goal",
        "description": "Validate requirements when the users request it. Typically activated by user inputs like 'ok', 'yes', 'next', or 'I'm done with it'.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "User requirements structured as list"
                }
            },
        "required": ["goal_list"]
        }
    }

    FUNCTION_REQUEST_SECOND_CONFIRMATION = {
        "name": "request_second_confirmation",
        "description": "Ask the user to confirm he validates the requirements yes/no question to confirm their decision.",
        "parameters": {
            "type": "object",
            "properties": {
                "confirmation_question": {
                    "type": "string",
                    "description": "A simple yes/no question crafted by to confirm the user's intent. It should be phrased in a way that encourages the user to either affirm their intent validate the current goals with a 'yes' or to reconsider with a 'no'."
                }
            },
            "required": ["confirmation_question"]
        }
    }


    default_configuration = RefineUserContextConfiguration(
        model_classification=LanguageModelClassification.FAST_MODEL_4K,
    )

    def __init__(
        self,
        logger : Logger,
        model_classification: LanguageModelClassification,
        # system_prompt: str,
        # user_prompt_template: str,
        # strategy_functions: str,
        # min_tokens: int,
        # max_tokens: int,
    ):
        self._logger = logger
        self._model_classification = model_classification
        #self._system_prompt_message = system_prompt
        # self._user_prompt_template = user_prompt_template
        #self._strategy_functions = strategy_functions
        # self._min_tokens : int = min_tokens
        # self._max_tokens : int = max_tokens
        # NOTE : Make a Dictionary ?
        self.question_history_full : list[str] = []
        self._last_questions = []
        self._user_last_goal = ''
        self._count = 0



    def build_prompt(self, user_objective: str = "", **kwargs) -> LanguageModelPrompt:
        #
        # STEP 1 : List all functions available
        #
        Re =LanguageModelFunction(
            **RefineUserContext.FUNCTION_REFINE_USER_CONTEXT,
        )
        Se= LanguageModelFunction(
            **RefineUserContext.FUNCTION_REQUEST_SECOND_CONFIRMATION,
        )
        Va =LanguageModelFunction(
            **RefineUserContext.FUNCTION_VALIDATE_GOAL,
        )
        strategy_functions =  [Re,Se ,Va]
        
        #
        # Step 2 A : Build the Sytem Promp
        #
        self._system_prompt_message = self.SYSTEM_PROMPT_INIT
        if not self._last_questions or not self._user_last_goal:
            self._system_prompt_message += self.NEW_SYSTEM_PROMPT
        else :
            if len(self._last_questions) == len(self.question_history_full): 
                self._system_prompt_message += self.REFINED_SYSTEM_PROMPT
            else : 
                self._system_prompt_message += self.REFINED_ONCE_SYSTEM_PROMPT
        self._system_prompt_message += self.SYSTEM_PROMPT_FOOTER

        system_message = LanguageModelMessage(
            role=MessageRole.SYSTEM,
            content=self._system_prompt_message.format(
                 user_last_goal = self._user_last_goal,
                 questions_history_full= to_numbered_list( [item['question'] for item in self.question_history_full]),
                 last_questions  = to_numbered_list([item['question'] for item in self._last_questions]),
                 user_response  = user_objective,
            ),
        )

        #
        # STEP 2 : A message from the user
        # NOTE : Keep the commented line for explanation to ilmplement further prompts
        #
        system_warning = LanguageModelMessage(
            role=MessageRole.SYSTEM,
            content=self.SYSTEM_PROMPT_NOTICE
            )

        assistant_acknowledgement = LanguageModelMessage(
            role=MessageRole.ASSISTANT,
            content= "Ok ! I will only answer using one of this functions : \n {functions_list}".format(
                functions_list = to_numbered_list([item.name for item in strategy_functions])
                )        
            )

        messages = [system_message, system_warning, assistant_acknowledgement]

        #
        # Step 3 : Build de prompt
        #

        # NOTE : Avoid Alucinations 
        function_call = 'auto'
        if self._count == 0 : 
           function_call =  'refine_goal'

        prompt = LanguageModelPrompt(
            #messages=[system_message, user_message],
            messages=messages,
            functions=strategy_functions,
            function_call =  function_call, 
            # TODO
            tokens_used=0,
        )
        #self._logger.debug('Executing prompt : ' + str(prompt))
        return prompt

    def parse_response_content(
        self,
        response_content: dict,
    ) -> dict:
        """Parse the actual text response from the objective model.

        Args:
            response_content: The raw response content from the objective model.

        Returns:
            The parsed response.

        """
        try : 
            parsed_response = json_loads(response_content["function_call"]['arguments'])
        except Exception :
            print('bad luck')


        #
        # Give id to questions
        # TODO : Type Questions in a Class ?
        #
        save_questions = False 
        if response_content["function_call"]["name"] == "refine_goal":

            questions_with_uuid = [{"id": "Q" + str(uuid.uuid4()), "question": q} for q in parsed_response["questions"]]
            save_questions = True 

            #
            # Saving the last goal
            #
            self._user_last_goal = parsed_response['reformulated_goal']
        elif  response_content["function_call"]["name"] == 'request_second_confirmation' :
            questions_with_uuid = [{"id": "Q" + str(uuid.uuid4()), "question":  parsed_response["confirmation_question"]}]
            save_questions = True 

        #
        # Saving the questions
        #
        if save_questions :
            self.question_history_full.extend(questions_with_uuid)
            self._last_questions = questions_with_uuid
            

        parsed_response['name'] = response_content["function_call"]["name"]
        self._logger.debug(parsed_response)
        self._count += 1 
        return parsed_response
    
    # TODO : This implementation is shit :) 
    # + Move to BasePromptStrategy
    # @staticmethod
    # def get_functions() :
    #     Re =LanguageModelFunction(
    #         **RefineUserContext.FUNCTION_REFINE_USER_CONTEXT,
    #     )
    #     Se= LanguageModelFunction(
    #         **RefineUserContext.FUNCTION_REQUEST_SECOND_CONFIRMATION,
    #     )
    #     Va =LanguageModelFunction(
    #         **RefineUserContext.FUNCTION_VALIDATE_GOAL,
    #     )
    #     return [Re,Se ,Va]
        
    # TODO : This implementation is shit :) 
    # + Move to BasePromptStrategy
    # @staticmethod
    # def get_functions_name() :
    #     re = [Re,Se ,Va]
        
