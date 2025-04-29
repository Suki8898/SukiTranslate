const API_KEY = 'YOUR_TOKEN_HERE'; // Replace with your Github API key https://github.com/settings/tokens
const MODEL = 'gpt-4o-mini'; // Models https://github.com/marketplace/models , rate limits https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits
const API_URL = 'https://models.inference.ai.azure.com/chat/completions';
const MAX_TOKENS = 2000;
const TEMPERATURE = 0.5; // Controls the randomness of the output, lower values are more deterministic and higher values are more random (0 - 1)

const fs = require('fs');
const fetch = require('node-fetch');

async function translate(text, sourceLang, targetLang) {
    const prompt = `Translate everything inside the angle brackets <<>> from ${sourceLang} to ${targetLang} and return only the translated text, without the angle brackets: << ${text} >>`;
    const requestBody = {
        model: MODEL,
        temperature: TEMPERATURE, 
        max_tokens: MAX_TOKENS,
        messages: [{ role: "user", content: prompt }],
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
    getTranslatedText
};
