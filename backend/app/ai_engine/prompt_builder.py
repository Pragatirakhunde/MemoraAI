from typing import Any


class PromptBuilder:

    @staticmethod
    def build_grounded_prompt(
        query: str,
        fused_context: list[dict[str, Any]],
        entities: list[dict[str, Any]] | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> str:

        # -------------------------------------------------
        # Build retrieved context
        # -------------------------------------------------

        context_parts = []

        for index, item in enumerate(fused_context, start=1):
            source_type = item.get("source_type", "unknown")
            content = item.get("content", "")
            reference = item.get("reference") or {}

            title = reference.get("title", "Unknown")
            file_path = reference.get("file_path", "Unknown")

            context_parts.append(
                f"""
SOURCE {index}
Type: {source_type}
Title: {title}
File: {file_path}

Content:
{content}
"""
            )

        context_text = "\n".join(context_parts)

        # -------------------------------------------------
        # Build detected entity information
        # -------------------------------------------------

        entity_text = ""

        if entities:
            entity_names = [
                entity.get("name")
                for entity in entities
                if entity.get("name")
            ]

            if entity_names:
                entity_text = (
                    "\nRelevant entities detected:\n"
                    + ", ".join(entity_names)
                    + "\n"
                )

        # -------------------------------------------------
        # Build conversation history
        # -------------------------------------------------

        history_parts = []

        if conversation_history:
            for message in conversation_history[-10:]:
                role = message.get("role", "user")
                content = message.get("content", "")

                history_parts.append(
                    f"{role.upper()}: {content}"
                )

        history_text = "\n".join(history_parts)

        # -------------------------------------------------
        # Final grounded prompt
        # -------------------------------------------------

        prompt = f"""
You are the AI assistant for an organization's internal knowledge system.

Your task is to answer the user's question using ONLY the organizational
knowledge provided in the retrieved context.

STRICT RULES:
1. Use the retrieved context as the primary source of truth.
2. Do not invent projects, technologies, people, APIs, decisions, or facts.
3. Do not use unsupported assumptions as facts.
4. If the retrieved context does not contain enough information, clearly say
   that the available organizational knowledge is insufficient.
5. Combine information from multiple sources when useful.
6. Keep the answer clear and concise.
7. Mention relevant source titles/files when appropriate.
8. Conversation history provides context, but it must not override
   retrieved organizational knowledge.

{entity_text}

USER QUESTION:
{query}

CONVERSATION HISTORY:
{history_text if history_text else "No previous conversation."}

RETRIEVED ORGANIZATIONAL CONTEXT:
{context_text if context_text else "No relevant organizational context was retrieved."}
"""

        return prompt.strip()