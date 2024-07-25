import streamlit as st
from langchain_groq import ChatGroq
llm = ChatGroq(temperature=0.5, groq_api_key="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", model_name="llama3-70b-8192")

# Define the extractor function
def extractor(llm, query):
    prompt = f'''
    Extract the following parameters from the given e-commerce query:
    
    Query: "{query}"
    
    **Instructions:**
    Identify and extract the following details from the query:
    - **Categories**: Check if the query mentions any of the following categories: Jeans, Shirt, Tshirts, Footwear, Watches.
    - **Product Name**: The name of the product(s).
    - **Color**: The color(s) mentioned for the product(s).
    - **Size**: The size(s) mentioned for the product(s).
    
    If a detail is not mentioned in the query, respond with "NA".

    Respond with the information in the following format:
    
    CATEGORIES: "Categories separated by commas or NA"
    PRODUCT_NAME: "Product name(s) separated by commas or NA"
    COLOR: "Colors separated by commas or NA"
    SIZE: "Sizes separated by commas or NA"
    '''
    
    response = llm.invoke(prompt)
    return response.content

# Define the parser function
def parser(response):
    parsed_data = {
        "CATEGORIES": "NA",
        "PRODUCT_NAME": "NA",
        "COLOR": "NA",
        "SIZE": "NA"
    }

    lines = response.split('\n')
    current_key = None

    for line in lines:
        line = line.strip()
        if line:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"')
                if key in parsed_data:
                    parsed_data[key] = value
                    current_key = key
            elif current_key:
                # If there's no colon, it's a continuation of the previous value
                parsed_data[current_key] += " " + line.strip('"')

    return parsed_data

# Define the function to count the number of "NA"
def count_na(parsed_data):
    return sum(1 for value in parsed_data.values() if value == "NA")

# Define the function to generate a follow-up prompt
def follow_up_prompt(parsed_data):
    missing_parameters = [key for key, value in parsed_data.items() if value == "NA"]
    missing_parameters_str = ', '.join(missing_parameters)
    
    prompt = f'''
    You have not mentioned the following parameters: {missing_parameters_str}.
    Would you like to provide more details about these parameters? If so, please provide the additional information.
    '''
    
    return prompt

# Streamlit app
def main():
    st.title("E-commerce Query Extractor")
    
    
    query = st.text_area("Enter your e-commerce query:")
    
    if st.button("Extract Details"):
        if query:
            response = extractor(llm, query)
            parsed_data = parser(response)
            
            st.subheader("Extracted Details:")
            st.write("**Categories:**", parsed_data["CATEGORIES"])
            st.write("**Product Name:**", parsed_data["PRODUCT_NAME"])
            st.write("**Color:**", parsed_data["COLOR"])
            st.write("**Size:**", parsed_data["SIZE"])
            
            na_count = count_na(parsed_data)
            st.write(f"**Number of 'NA' parameters:** {na_count}")
            
            if na_count > 0:
                follow_up = st.text_input(follow_up_prompt(parsed_data))
                
                if st.button("Provide Additional Details"):
                    if follow_up:
                        follow_up_response = extractor(llm, follow_up)
                        follow_up_data = parser(follow_up_response)
                        
                        for key in parsed_data:
                            if parsed_data[key] == "NA" and follow_up_data[key] != "NA":
                                parsed_data[key] = follow_up_data[key]
                        
                        st.subheader("Updated Extracted Details:")
                        st.write("**Categories:**", parsed_data["CATEGORIES"])
                        st.write("**Product Name:**", parsed_data["PRODUCT_NAME"])
                        st.write("**Color:**", parsed_data["COLOR"])
                        st.write("**Size:**", parsed_data["SIZE"])
        else:
            st.error("Please enter a query.")

if __name__ == "__main__":
    main()
