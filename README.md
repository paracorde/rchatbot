# 28 Restaurant Management System

A restaurant management system for 28 Restaurant with an AI-powered chatbot interface. This system allows customers to book tables, place orders, and receive personalized menu recommendations through natural language interactions.

## Features

- **Natural Language Interface**: Interact with the restaurant system using everyday language
- **Table Booking**: Check availability and reserve tables based on party size and time
- **Food Ordering**: Place orders with automatic allergen detection
- **Smart Recommendations**: Receive personalized menu suggestions based on preferences
- **Allergen Safety**: Prevents orders containing allergens that customers are allergic to
- **Business Hour Awareness**: Respects restaurant opening hours for availability

<!-- ## Demo

![Screenshot of the 28 Restaurant Management System](screenshot.png) -->

## Setup Instructions

### Prerequisites

- Python 3.8+
- Azure OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/paracorde/rchatbot.git
   cd rchatbot
   ```

2. Install dependencies:
   ```
   pip install streamlit openai
   ```

3. Run the application:
   ```
   streamlit run chatbot.py
   ```

4. Enter your Azure OpenAI API key in the sidebar when prompted

## Usage Examples

### Booking a Table

User: "Can I book a table for 4 people on Saturday at 7 PM?"

The system will:
1. Check availability for the requested time
2. Present available time slots
3. Confirm the booking
4. Provide a table number

### Placing an Order

User: "I'd like to order two burgers and a diet coke. I'm allergic to soy."

The system will:
1. Identify menu items and quantities
2. Check for allergen conflicts
3. Calculate the total cost and preparation time
4. Confirm the order if no allergens conflict with the user's allergies

### Getting Recommendations

User: "What would you recommend for a quick lunch that doesn't contain gluten?"

The system will:
1. Extract preferences and allergies
2. Find suitable menu items
3. Provide personalized recommendations

## System Architecture

### Components

1. **Chatbot Interface** (`chatbot.py`):
   - Streamlit-based UI
   - Azure OpenAI integration
   - Session state management

2. **Restaurant Backend** (`restaurant.py`):
   - Table reservation system
   - Order processing
   - Menu management
   - Booking and availability logic

### Data Flow

1. User interacts with the system using natural language
2. The OpenAI model processes the request and formats it as a structured command
3. The backend executes the command and returns a response
4. The response is presented to the user in a conversational format

## Configuration

The restaurant system comes pre-configured with:

- **Table sizes**: 2-seat (4 tables), 4-seat (4 tables), 8-seat (2 tables)
- **Opening hours**: Daily, stored in 15-minute time blocks
- **Menu**: Basic menu with fries, burger, and diet coke
- **Allergen tracking**: Automatically checks for gluten, dairy, and soy allergies

## API Integration

The system uses the Azure OpenAI API with the GPT-4o model for natural language processing. You'll need to provide your own API key to use the system.

## Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your Azure OpenAI API key is entered correctly in the sidebar
- **Reservation Errors**: Reservations must be in 15-minute blocks and cannot be made in the past
- **Order Processing**: Items must match menu items exactly; the system will ask for clarification otherwise

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the language model capabilities
- Streamlit for the interactive web interface 