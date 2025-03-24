from flask import Flask, request, Response, jsonify
import asyncio
from langgraph.graph import StateGraphExecutor
from langchain_core.messages import HumanMessage
from configuration import Configuration 
from scalema_omni import graph

app = Flask(__name__)

# Create an executor from your compiled graph
executor = StateGraphExecutor(graph)


async def langgraph_streaming_response(user_input, config):
    """Handles streaming responses from LangGraph."""
    async for chunk in executor.astream({"messages": [
            HumanMessage(content=user_input)]}, config=config):
        yield chunk["messages"][0]["content"] + "\n"  # Extract text content


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Streams chatbot responses to Django."""
    try:
        data = request.get_json()
        user_input = data.get("query")
        config = data.get("config", {})

        async def generate():
            async for chunk in langgraph_streaming_response(user_input, config):
                yield chunk

        return Response(generate(), content_type="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test", methods=["POST"])
def test_api():
    return 'i am here'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
