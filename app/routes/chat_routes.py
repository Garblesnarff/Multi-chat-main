"""
chat_routes.py - Chat endpoints for multi-provider LLM app

Defines Flask routes for chat interactions, including streaming and reasoning support.

Dependencies:
- flask (Blueprint, render_template, request, jsonify, session, Response, stream_with_context)
- logging
- json
- app.routes.provider_factory.get_llm_provider

@author Auto-refactored by Cline
"""

from flask import Blueprint, render_template, request, jsonify, session, Response, stream_with_context
import logging
import json

from app.routes.provider_factory import get_llm_provider

chat_bp = Blueprint('chat', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@chat_bp.route('/')
def index():
    """
    Render the main chat UI.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('index.html')

@chat_bp.route('/chat', methods=['POST', 'GET'])
def chat():
    """
    Handle chat requests, supporting streaming and reasoning.

    POST or GET parameters:
        message (str): User message.
        providers (dict): Provider names mapped to model names.
        use_reasoning (bool): Whether to include reasoning.
        use_streaming (bool): Whether to stream responses.

    Returns:
        JSON response or streaming response.
    """
    try:
        if request.method == 'GET':
            message = request.args.get('message')
            providers = json.loads(request.args.get('providers'))
            use_reasoning = request.args.get('use_reasoning') == 'true'
            use_streaming = request.args.get('use_streaming') == 'true'
        else:
            data = request.json
            message = data.get('message')
            providers = data.get('providers', {})
            use_reasoning = data.get('use_reasoning', False)
            use_streaming = data.get('use_streaming', False)

        logger.debug(f"Received chat request: message={message}, providers={providers}, use_reasoning={use_reasoning}, use_streaming={use_streaming}")

        if 'llm_provider' not in session:
            session['llm_provider'] = {}

        if use_streaming:
            def generate():
                try:
                    for provider, model in providers.items():
                        yield f"data: {provider}\n\n"
                        llm = get_llm_provider(provider)
                        for chunk in llm.generate_stream(message, model, use_reasoning):
                            yield f"data: {chunk}\n\n"
                        yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Error in generate function: {str(e)}")
                    yield f"data: Error: {str(e)}\n\n"
            return Response(stream_with_context(generate()), content_type='text/event-stream')
        else:
            responses = {}
            for provider, model in providers.items():
                llm = get_llm_provider(provider)
                try:
                    if use_reasoning:
                        responses[provider] = llm.generate_response_with_reasoning(message, model)
                    else:
                        responses[provider] = llm.generate_response(message, model)
                    session['llm_provider'][provider] = llm.to_dict()
                except Exception as e:
                    logger.error(f"Error generating response for provider {provider}: {str(e)}")
                    responses[provider] = f"Error: {str(e)}"
            
            return jsonify({'responses': responses})
    except Exception as e:
        logger.error(f"Unexpected error in chat route: {str(e)}")
        if 'use_streaming' in locals() and use_streaming:
            def generate():
                yield f"data: Error: {str(e)}\n\n"
            return Response(stream_with_context(generate()), content_type='text/event-stream')
        else:
            return jsonify({'error': str(e)}), 500
