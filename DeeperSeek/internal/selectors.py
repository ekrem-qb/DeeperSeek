from dataclasses import dataclass

@dataclass
class DeepSeekSelectors:    
    # Login
    email_input_css = 'input[type="text"]'
    password_input_css = 'input[type="password"]'
    confirm_checkbox_css = 'div[class="ds-checkbox ds-checkbox--none ds-checkbox--bordered"]'
    login_button_css = 'div[role="button"]'

    # Interactions
    textbox_css = 'textarea[class="c92459f0"]'
    send_options_parent_css = 'div[class="ec4f5d61"]'
    send_button_css = 'div[class="f6d670"]'
    deepthink_button_css = 'div[class="d9f56c96"]'
    search_button_css = 'div[class="ad0c98fd"]'
    response_toolbar_css = 'div[class="ds-flex abe97156"]'
    """First div: **copy** `||` Second div: **regenerate** `||` Third div: **like** `||` Fourth div: **dislike**"""
    reset_chat_button_css = 'div[class="e214291b"]'

    # Response data
    first_extra_option_css = 'div[class="a6d716f5 db5991dd"]'
    second_extra_option_css = 'div[class="edb250b1"]'

    # Backend
    conversation_css = 'div[class="dad65929"]'
    response_generating_css = 'div[class="f9bf7997 d7dc56a8"]'
    response_generated_css = 'div[class="f9bf7997 d7dc56a8 c05b5566"]'
    response_css = 'ds-markdown' # This is different, because its used in BS4
    regen_loading_icon_css = 'div[class="ds-loading b4e4476b"]'
    response_toolbar_b64_css = 'ds-flex abe97156' # This is different, because its used in BS4

    # Search results
    search_results_div = 'div[class="fe369d61 f529c936"]'

    # DeepThink
    deepthink_content_css = 'div[class="e1675d8b"]'
    deepthink_pTags_css = 'ba94db8a'
    
    # URLs
    chat_url = "https://chat.deepseek.com/"
