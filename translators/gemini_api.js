const API_KEY = 'YOUR_API_KEY_HERE'; // Replace with your Gemini API key https://aistudio.google.com/app/apikey
const MODEL = 'gemini-2.0-flash'; // Models and pricing https://ai.google.dev/gemini-api/docs/models https://ai.google.dev/gemini-api/docs/pricing
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}`;
const MAX_TOKENS = 2000;
const TEMPERATURE = 0.5; // Controls the randomness of the output, lower values are more deterministic and higher values are more random (0 - 2)

const fs = require('fs');
const fetch = require('node-fetch');

async function translate(text, sourceLang, targetLang) {
    const prompt = `Translate everything inside the angle brackets <<>> from ${sourceLang} to ${targetLang} and return only the translated text, without the angle brackets: << ${text} >>`;
    const requestBody = {
        contents: [{
            parts: [{
                text: prompt
            }]
        }],
        generationConfig: {
        temperature: TEMPERATURE,
        maxOutputTokens: MAX_TOKENS
        },
        safetySettings: [
            {
                category: "HARM_CATEGORY_HARASSMENT",
                threshold: "OFF",
            },
            {
                category: "HARM_CATEGORY_HATE_SPEECH",
                threshold: "OFF",
            },
            {
                category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold: "OFF",
            },
            {
                category: "HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold: "OFF",
            },
            {
                category: "HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold: "OFF",
            }
        ],
    };

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    });

    

    if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
    }
    const data = await response.json();
    const translatedText = data.candidates?.[0]?.content?.parts?.[0]?.text?.trim();
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
