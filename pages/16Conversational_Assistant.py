"""
Natural Language Conversational Assistant for Logistics Cost Estimation

This module provides an AI-powered chat interface that allows users to:
- Query logistics data using natural language
- Get cost calculations and comparisons
- Receive guidance on using the application
- Generate reports and visualizations through conversation

This version has been adapted to use a local LLM (e.g., Llama 3) instead of the
OpenAI API. A path to the local model file must be provided via the
``LLAMA_MODEL_PATH`` environment variable. If the model cannot be loaded,
the assistant will fall back to a limited command‑based mode.
"""

import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional
import re

# Import application modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.calculations import LogisticsCostCalculator
from utils.validators import MaterialValidator, SupplierValidator

# We no longer import openai; instead we will load a local LLM model via
# llama‑cpp‑python. If the model cannot be loaded, the assistant will operate
# in a reduced capacity (only basic commands).
try:
    from llama_cpp import Llama  # type: ignore
except ImportError:
    Llama = None  # type: ignore

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConversationalAssistant:
    """
    Natural language interface for the logistics cost application.
    Uses a local LLM (e.g., Llama 3) for understanding queries and generating
    responses. If no local model is configured, the assistant will only
    support a limited set of predefined commands.
    """

    def __init__(self):
        self.data_manager = DataManager()
        self.calculator = LogisticsCostCalculator()
        # Initialise the LLM and availability flag
        self.llm = None
        self.api_available = False
        self.setup_openai()  # repurposed to load the local model
        self.initialize_session_state()

    def setup_openai(self):  # noqa: D401 – retained name for backwards compatibility
        """Configure the local LLM model.

        This method attempts to load a gguf model specified by the
        ``LLAMA_MODEL_PATH`` environment variable. If the model cannot be
        loaded (e.g., missing dependency or file), the assistant will fall
        back to basic command handling and display a warning to the user.
        """
        # Attempt to load the local LLM if llama_cpp is available
        model_path = os.getenv("LLAMA_MODEL_PATH")
        if Llama is None:
            st.warning(
                "⚠️ The `llama_cpp` library is not installed. Please install ``llama-cpp-python`` "
                "and ensure it is available in your environment to enable AI chat functionality."
            )
            self.api_available = False
            return
        if not model_path:
            st.warning(
                "⚠️ Local LLM model path not found. Please set LLAMA_MODEL_PATH in your .env file"
            )
            self.api_available = False
            return
        try:
            # Load the model. We do not specify a chat_format explicitly; the
            # model metadata should provide the appropriate template. Increase
            # context length if required by your model.
            self.llm = Llama(model_path=model_path)
            self.api_available = True
        except Exception as e:
            st.warning(f"⚠️ Failed to load LLM model: {e}")
            self.api_available = False

    def initialize_session_state(self):
        """Initialize chat history in session state."""
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'chat_context' not in st.session_state:
            st.session_state.chat_context = self.get_system_context()

    def get_system_context(self) -> str:
        """Build system context with current application state."""
        materials = self.data_manager.get_materials()
        suppliers = self.data_manager.get_suppliers()

        context = f"""You are a helpful assistant for a logistics cost estimation application.
        
Current system state:
- Materials configured: {len(materials)}
- Suppliers configured: {len(suppliers)}
- Material-supplier pairs: {len(self.data_manager.get_material_supplier_pairs())}

Available capabilities:
1. Query materials and suppliers data
2. Calculate logistics costs for specific pairs
3. Compare costs between different configurations  
4. Generate reports and visualizations
5. Guide users through configuration process
6. Explain cost components and calculations

When answering:
- Be concise but thorough
- Use specific data from the system when available
- Format numbers appropriately (currency, percentages)
- Suggest next steps when appropriate
"""

        # Add material details if available
        if materials:
            context += "\n\nAvailable materials:\n"
            for mat in materials[:5]:  # Show first 5
                context += f"- {mat['material_no']}: {mat['material_desc']} (Annual vol: {mat.get('annual_volume', 0):,})\n"

        # Add supplier details if available  
        if suppliers:
            context += "\n\nAvailable suppliers:\n"
            for sup in suppliers[:5]:  # Show first 5
                context += f"- {sup['vendor_id']}: {sup['vendor_name']} ({sup['vendor_country']})\n"

        return context

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process natural language query and determine intent and required data.
        """
        query_lower = query.lower()

        # Pattern matching for common queries
        patterns = {
            'list_materials': r'(list|show|display|what are).*(materials?|products?)',
            'list_suppliers': r'(list|show|display|what are).*(suppliers?|vendors?)',
            'calculate_cost': r'(calculate|compute|what is|find).*(cost|price)',
            'compare_costs': r'(compare|difference|which is cheaper)',
            'total_cost': r'(total|overall|sum|aggregate).*(cost|price)',
            'cheapest': r'(cheapest|lowest|minimum|best price)',
            'expensive': r'(expensive|highest|maximum|worst price)',
            'help': r'(help|how do|how to|guide|tutorial)',
            'status': r'(status|summary|overview|ready)',
            'export': r'(export|download|save|generate report)'
        }

        intent = 'general'
        entities: Dict[str, Any] = {}

        for pattern_name, pattern in patterns.items():
            if re.search(pattern, query_lower):
                intent = pattern_name
                break

        # Extract material numbers from query
        material_pattern = r'[A-Z]\d{6}'  # Pattern like K038600
        material_matches = re.findall(material_pattern, query.upper())
        if material_matches:
            entities['materials'] = material_matches

        # Extract supplier IDs from query
        supplier_pattern = r'\b\d{6}\b'  # 6-digit supplier IDs
        supplier_matches = re.findall(supplier_pattern, query)
        if supplier_matches:
            entities['suppliers'] = supplier_matches

        return {'intent': intent, 'entities': entities, 'original_query': query}

    def execute_intent(self, parsed_query: Dict[str, Any]) -> str:
        """
        Execute the identified intent and return response.
        """
        intent = parsed_query['intent']
        entities = parsed_query['entities']

        if intent == 'list_materials':
            return self.list_materials()
        elif intent == 'list_suppliers':
            return self.list_suppliers()
        elif intent == 'calculate_cost':
            return self.calculate_costs(entities)
        elif intent == 'compare_costs':
            return self.compare_costs(entities)
        elif intent == 'total_cost':
            return self.get_total_costs()
        elif intent == 'cheapest':
            return self.find_cheapest()
        elif intent == 'expensive':
            return self.find_most_expensive()
        elif intent == 'status':
            return self.get_system_status()
        elif intent == 'help':
            return self.provide_help()
        elif intent == 'export':
            return self.export_guidance()
        else:
            return self.handle_general_query(parsed_query['original_query'])

    def list_materials(self) -> str:
        """List all configured materials."""
        materials = self.data_manager.get_materials()
        if not materials:
            return "No materials configured yet. You can add materials in the Material Information page."

        response = f"**{len(materials)} Materials Configured:**\n\n"
        for mat in materials:
            response += f"• **{mat['material_no']}** - {mat['material_desc']}\n"
            response += f"  - Weight: {mat.get('weight_per_pcs', 0):.3f} kg/piece\n"
            response += f"  - Annual Volume: {mat.get('annual_volume', 0):,} pieces\n"
            response += f"  - Project: {mat.get('project_name', 'N/A')}\n\n"

        return response

    def list_suppliers(self) -> str:
        """List all configured suppliers."""
        suppliers = self.data_manager.get_suppliers()
        if not suppliers:
            return "No suppliers configured yet. You can add suppliers in the Supplier Information page."

        response = f"**{len(suppliers)} Suppliers Configured:**\n\n"
        for sup in suppliers:
            response += f"• **{sup['vendor_id']}** - {sup['vendor_name']}\n"
            response += f"  - Location: {sup['city_of_manufacture']}, {sup['vendor_country']}\n"
            response += f"  - Deliveries/Month: {sup.get('deliveries_per_month', 0)}\n\n"

        return response

    def calculate_costs(self, entities: Dict) -> str:
        """Calculate costs for specified materials/suppliers."""
        materials = self.data_manager.get_materials()
        suppliers = self.data_manager.get_suppliers()

        if not self.data_manager.is_calculation_ready():
            return "⚠️ System is not ready for calculations. Please ensure all required configurations are complete."

        # Get configurations
        packaging = self.data_manager.get_packaging()
        transport = self.data_manager.get_transport()
        warehouse = self.data_manager.get_warehouse()
        co2 = self.data_manager.get_co2()
        operations = self.data_manager.get_operations()
        locations = self.data_manager.get_locations()
        repacking = self.data_manager.get_repacking()
        customs = self.data_manager.get_customs()

        # Use first available configs
        result = self.calculator.calculate_total_logistics_cost(
            material=materials[0] if materials else {},
            supplier=suppliers[0] if suppliers else {},
            packaging_config=packaging[0] if packaging else {},
            transport_config=transport[0] if transport else {},
            warehouse_config=warehouse[0] if warehouse else {},
            repacking_config=repacking[0] if repacking else {},
            customs_config=customs[0] if customs else {},
            co2_config=co2[0] if co2 else {},
            operations_config=operations[0] if operations else {},
            location_config=locations[0] if locations else {}
        )

        if result:
            response = "**Logistics Cost Calculation Result:**\n\n"
            response += f"Material: {result['material_id']} - {result['material_desc']}\n"
            response += f"Supplier: {result['supplier_id']} - {result['supplier_name']}\n\n"
            response += "**Cost Breakdown (per piece):**\n"
            response += f"• Packaging: €{result['packaging_cost_per_piece']:.3f}\n"
            response += f"• Transport: €{result['transport_cost_per_piece']:.3f}\n"
            response += f"• Warehouse: €{result['warehouse_cost_per_piece']:.3f}\n"
            response += f"• Customs: €{result['customs_cost_per_piece']:.3f}\n"
            response += f"• CO₂: €{result['co2_cost_per_piece']:.3f}\n"
            response += f"• Repacking: €{result['repacking_cost_per_piece']:.3f}\n\n"
            response += f"**Total Cost per Piece: €{result['total_cost_per_piece']:.3f}**\n"
            response += f"**Total Annual Cost: €{result['total_annual_cost']:,.2f}**"
            return response
        else:
            return "Unable to calculate costs. Please check your configurations."

    def find_cheapest(self) -> str:
        """Find the cheapest material-supplier combination (placeholder implementation)."""
        if not self.data_manager.is_calculation_ready():
            return "System is not ready for calculations."

        # Calculate all combinations
        materials = self.data_manager.get_materials()
        suppliers = self.data_manager.get_suppliers()

        if not materials or not suppliers:
            return "Need at least one material and supplier configured."

        # The detailed implementation would iterate through all combinations.
        return "**Cost Analysis:**\nUse the Cost Calculation page for comprehensive analysis of all material-supplier combinations."

    def get_system_status(self) -> str:
        """Get current system configuration status."""
        stats = self.data_manager.get_statistics()

        response = "**System Configuration Status:**\n\n"
        response += f"✅ **Ready for Calculations:** {'Yes' if stats['calculation_ready'] else 'No'}\n\n"
        response += "**Configured Items:**\n"
        response += f"• Materials: {stats['total_materials']}\n"
        response += f"• Suppliers: {stats['total_suppliers']}\n"
        response += f"• Packaging Configs: {stats['total_packaging']}\n"
        response += f"• Transport Configs: {stats['total_transport']}\n"
        response += f"• Warehouse Configs: {stats['total_warehouse']}\n"
        response += f"• CO₂ Configs: {stats['total_co2']}\n"

        if not stats['calculation_ready']:
            response += "\n**Missing Requirements:**\n"
            if stats['total_materials'] == 0:
                response += "• Add at least one material\n"
            if stats['total_suppliers'] == 0:
                response += "• Add at least one supplier\n"
            if stats['total_packaging'] == 0:
                response += "• Configure packaging\n"
            if stats['total_transport'] == 0:
                response += "• Configure transport\n"

        return response

    def provide_help(self) -> str:
        """Provide help and guidance."""
        return """**How to Use the Logistics Cost Application:**

1. **Configure Materials** 📦
   - Go to Material Information page
   - Enter product details, weights, and volumes
   
2. **Add Suppliers** 🏭
   - Go to Supplier Information page
   - Enter vendor details and delivery schedules
   
3. **Set Up Cost Components** 💰
   - Configure packaging, transport, warehouse costs
   - Add customs, CO₂, and additional costs as needed
   
4. **Run Calculations** 🧮
   - Go to Cost Calculation page
   - Select materials and suppliers to analyze
   - Export results to Excel or CSV

**Common Commands You Can Ask:**
- "List all materials"
- "Show suppliers"
- "Calculate total logistics cost"
- "What's the cheapest option?"
- "Export results"
- "System status"

Need specific help? Just ask about any feature!"""

    def handle_general_query(self, query: str) -> str:
        """
        Handle general queries using the local LLM if available.

        If the LLM is not loaded, provide a fallback response advising the user
        to use specific commands. Messages and context from recent chat
        exchanges are passed to the model to preserve conversation state.
        """
        if not self.api_available or self.llm is None:
            return (
                "I can help with basic queries. Try asking about materials, suppliers, "
                "costs, or type 'help' for guidance."
            )

        try:
            # Build the conversation context
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": st.session_state.chat_context},
                {"role": "user", "content": query},
            ]
            # Add recent chat history for additional context
            for msg in st.session_state.chat_messages[-5:]:  # Last 5 messages
                messages.append({"role": msg["role"], "content": msg["content"]})
            # Append the current query again to ensure it is the last message
            messages.append({"role": "user", "content": query})

            # Use the local model to generate a response. The `create_chat_completion`
            # method returns a dict with a structure similar to the OpenAI API.
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.2, # more deterministic and relevant to the data without any creative generative answrers that is not relate to the investigated topic
            )

            # Extract the assistant's reply
            return response["choices"][0]["message"]["content"]
        except Exception:
            # Provide a generic fallback if anything goes wrong
            return (
                f"I understand you're asking about: '{query}'. Please try rephrasing "
                "or use specific commands like 'list materials' or 'calculate costs'."
            )

    def export_guidance(self) -> str:
        """Provide guidance on exporting data."""
        return """**Export Options Available:**

1. **From Cost Calculation Page:**
   - Calculate costs first
   - Click "Download Results as CSV" or "Download Results as Excel"
   - Professional formatted reports with all cost breakdowns

2. **From Overview Page:**
   - Click "Export Configuration" to save all settings
   - JSON format for backup or sharing
   
3. **From This Chat:**
   - Copy any results displayed here
   - Or go to the Cost Calculation page for full export options

Would you like me to calculate something specific for you to export?"""

    def compare_costs(self, entities: Dict) -> str:
        """Compare costs between different configurations."""
        return """**Cost Comparison:**

To compare costs between different configurations:
1. Go to the Cost Calculation page
2. Run calculations for multiple material-supplier pairs
3. View the comparison table showing:
   - Cost per piece
   - Annual costs
   - Cost component breakdown
   
The system will highlight the best and worst options automatically.

Need specific comparison? Please specify the material numbers and supplier IDs."""


def main() -> None:
    """Main function for the Conversational Assistant page."""
    st.set_page_config(
        page_title="Conversational Assistant - Logistics Cost",
        page_icon="💬",
        layout="wide"
    )

    st.title("💬 Conversational Assistant")
    st.markdown("Ask questions about your logistics data in natural language")

    # Initialize assistant
    assistant = ConversationalAssistant()

    # Check LLM availability
    if not assistant.api_available:
        st.info("""ℹ️ **Limited Mode Active**
        
To enable full AI capabilities:
1. Install the `llama-cpp-python` library
2. Download a Llama model (e.g., from Hugging Face) in .gguf format
3. Create a `.env` file in the project root
4. Add: `LLAMA_MODEL_PATH=/path/to/your/model.gguf`

Currently available commands:
- "list materials" / "show suppliers"
- "calculate costs" / "system status"
- "help" / "export"
""")

    # Chat interface
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me anything about your logistics data..."):
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Process query and generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Parse and execute query
                parsed = assistant.process_query(prompt)
                response = assistant.execute_intent(parsed)

                st.markdown(response)

                # Add assistant response to history
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

    # Sidebar with quick actions
    with st.sidebar:
        st.markdown("### 🚀 Quick Actions")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 System Status"):
                response = assistant.get_system_status()
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("📦 List Materials"):
                response = assistant.list_materials()
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("🏭 List Suppliers"):
                response = assistant.list_suppliers()
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

        with col2:
            if st.button("💰 Calculate Costs"):
                response = assistant.calculate_costs({})
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("❓ Get Help"):
                response = assistant.provide_help()
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_messages = []
                st.rerun()

        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        - What materials do we have?
        - Show me all suppliers from Germany
        - Calculate logistics cost for K038600
        - What's the total annual cost?
        - Which supplier is cheapest?
        - How do I export results?
        - Is the system ready for calculations?
        """)

        st.markdown("---")
        st.markdown("### 📈 Statistics")
        stats = assistant.data_manager.get_statistics()
        st.metric("Materials", stats['total_materials'])
        st.metric("Suppliers", stats['total_suppliers'])
        st.metric("Ready", "Yes ✅" if stats['calculation_ready'] else "No ❌")


if __name__ == "__main__":
    main()