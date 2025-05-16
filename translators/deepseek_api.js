// Replace with your DeepSeek API key https://platform.deepseek.com/api_keys; // Replace with your DeepSeek API key https://platform.deepseek.com/api_keys
const API_KEY = 'YOUR_API_KEY_HERE';

// Models and pricing https://api-docs.deepseek.com/quick_start/pricing; // Models and pricing https://api-docs.deepseek.com/quick_start/pricing
const MODEL = 'deepseek-chat';

const API_URL = 'https://api.deepseek.com/v1/chat/completions';
const MAX_TOKENS = 2000;
const TEMPERATURE = 0.5; // Controls the randomness of the output, lower values are more deterministic and higher values are more random (0 - 2)

const fs = require('fs');
const fetch = require('node-fetch');

async function translate(text, sourceLang, targetLang) {

    const prompt = `Translate from ${sourceLang} to ${targetLang} and return only the translated text`;

    const requestBody = {
        model: MODEL,
        temperature: TEMPERATURE, 
        max_tokens: MAX_TOKENS,
        messages: [{
            role: "system",
            content: prompt
            }, {
            role: "user",
            content: text
        }] 
    };

const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
    }

    const data = await response.json();
    const translatedText = data.choices[0].message.content.trim();
    return translatedText;
}

async function translateImage(input) {
    try {
        const { image, sourceLang, targetLang } = JSON.parse(input);
        const prompt = `Translate from ${sourceLang} to ${targetLang} and return only the translated text`;
        
        const requestBody = {
            model: MODEL,
            temperature: TEMPERATURE,
            max_tokens: MAX_TOKENS,
            messages: [{
                role: "system",
                content: prompt
            }, {
                role: "user",
                content: [{
                    type: "image_url",
                    image_url: {
                        url: `data:image/png;base64,${image}`
                    }
                }]
            }]
        };

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`API request failed with status: ${response.status}`);
        }

        const data = await response.json();
        const translatedText = data.choices[0].message.content.trim();
        return translatedText;

    } catch (error) {
        console.error(`Error translating image: ${error}`);
        throw error;
    }
}

async function getTranslatedText(text, sourceLang, targetLang) {
    try {
        const translatedText = await translate(text, sourceLang, targetLang);
        return translatedText;
    } catch (error) {
        console.error(`Error translating text: ${error}`);
        throw error;
    }
}

module.exports = {
    getTranslatedText,
    translateImage
};
