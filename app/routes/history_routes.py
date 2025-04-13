"""
history_routes.py - Conversation history management endpoints

Defines Flask routes for clearing conversation history per provider.

Dependencies:
- flask (Blueprint, request, jsonify, session)
- app.routes.provider_factory.get_llm_provider

@author Auto-refactored by Cline
"""

from flask import Blueprint, request, jsonify, session

from app.routes.provider_factory import get_llm_provider

history_bp = Blueprint('history', __name__)

@history_bp.route('/clear_history', methods=['POST'])
def clear_history():
    """
    Clear the conversation history for a specific provider.

    POST JSON:
        provider (str): Provider name.

    Returns:
        JSON response with success or error message.
    """
    data = request.json
    provider = data.get('provider')

    if 'llm_provider' in session and provider in session['llm_provider']:
        session['llm_provider'][provider] = get_llm_provider(provider, new_instance=True).to_dict()
        return jsonify({'message': 'Conversation history cleared'}), 200
    else:
        return jsonify({'error': 'Invalid provider or no conversation history'}), 400
