# Code Summary

## Overview
This codebase implements a restaurant management system with an AI-powered chatbot interface. The system enables users to book tables, check availability, place food orders through natural language interaction, and receive personalized menu recommendations.

## Key Components

### 1. Restaurant Class (`restaurant.py`)
The core backend logic for managing restaurant operations:

- **Table Management**:
  - Supports different table sizes (2, 4, and 8 seats)
  - Tracks table availability in 15-minute time blocks
  - Handles reservation logic to prevent double-booking

- **Time Management**:
  - Converts between Unix timestamps and "restaurant time" (15-minute blocks)
  - Respects restaurant opening hours when determining availability

- **Booking System**:
  - Finds appropriate tables based on party size
  - Checks availability across specified time periods
  - Books tables and marks them as unavailable

- **Order Processing**:
  - Manages food orders from the menu
  - Calculates total cost and estimated preparation time
  - Tracks order queue and processes completion
  - **Allergy Awareness**: Prevents orders containing allergens that the user is allergic to

- **Recommendation System**:
  - Provides menu item suggestions based on user preferences
  - Filters recommendations to avoid items with allergens the user is allergic to
  - Leverages the LLM's understanding of context to provide personalized suggestions

- **Data Persistence**:
  - Provides JSON serialization/deserialization
  - Supports saving and loading restaurant state

### 2. Chatbot Interface (`chatbot.py`)
A Streamlit-based user interface that leverages OpenAI's models:

- **Natural Language Processing**:
  - Uses Azure OpenAI API (GPT-4o) to understand user requests
  - Processes natural language into actionable commands

- **Conversational UI**:
  - Maintains conversation history in the session state
  - Displays chat interaction in a user-friendly interface

- **Integration Layer**:
  - Translates between natural language and backend operations
  - Uses a special JSON format for structured commands
  - Handles query processing and response formatting
  - Identifies and processes allergy information in user queries

### 3. Menu System
Basic menu with several items, each containing:
- Price information
- Preparation time
- Description
- Allergen information
- Current items:
  - Fries ($20) - Contains gluten
  - Burger ($40) - Contains gluten, dairy, soy
  - Diet Coke ($10) - No allergens

## Key Workflows

1. **Table Booking**:
   - User inquires about availability for a specific date, time, and party size
   - System checks available time slots
   - User confirms desired time
   - System books the table and returns confirmation

2. **Food Ordering**:
   - User places order in natural language
   - System identifies menu items, quantities, and potential allergies
   - Backend checks for allergen conflicts
   - System either processes the order or informs of allergen issues
   - User receives order confirmation with details when successful

3. **Menu Recommendations**:
   - User asks for recommendations, possibly including preferences
   - System extracts preferences and allergies from the query
   - Backend provides menu data matching user criteria
   - LLM generates personalized recommendations based on context

## Technical Implementation

- **Time Representation**: Uses 15-minute blocks for scheduling
- **Table Assignment**: Optimizes table usage by assigning appropriate sizes
- **State Management**: Maintains session state between interactions
- **Error Handling**: Validates requests and prevents invalid operations
- **Allergy Safety**: Prevents orders of items containing allergens the user is allergic to

The system demonstrates a practical application of conversational AI for business operations, combining natural language processing with structured backend functionality and safety features. 