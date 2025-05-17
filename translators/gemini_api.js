// Replace with your Gemini API key https://aistudio.google.com/app/apikey
const API_KEY = 'YOUR_API_KEY_HERE';

// Models and pricing https://ai.google.dev/gemini-api/docs/models https://ai.google.dev/gemini-api/docs/pricing
const MODEL = 'gemini-2.0-flash';

const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}`;
const MAX_TOKENS = 2000;
const TEMPERATURE = 0.5; // Controls the randomness of the output, lower values are more deterministic and higher values are more random (0 - 2)

const fs = require('fs');
const fetch = require('node-fetch');

async function translate(text, sourceLang, targetLang) {
    const prompt = `Translate from ${sourceLang} to ${targetLang} and return only the translated text`;

    const requestBody = {
        system_instruction: {
            parts: [{
                text: prompt
            }]
        },
        contents: {
            parts: [{
                text: text
            }]
        },
        generationConfig: {
            temperature: TEMPERATURE,
            maxOutputTokens: MAX_TOKENS
        },
        safetySettings: [
            {
                category: "HARM_CATEGORY_HARASSMENT",
                threshold: "BLOCK_NONE"
            },
            {
                category: "HARM_CATEGORY_HATE_SPEECH",
                threshold: "BLOCK_NONE"
            },
            {
                category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold: "BLOCK_NONE"
            },
            {
                category: "HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold: "BLOCK_NONE"
            }
        ]
    };

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
    }

    const data = await response.json();
    const translatedText = data.candidates?.[0]?.content?.parts?.[0]?.text?.trim();
    if (!translatedText) {
        throw new Error('No translated text found in response');
    }
    return translatedText;
}

async function translateImage(input) {
    try {
        const { image, sourceLang, targetLang } = JSON.parse(input);
        const prompt = `Extract the text from the provided image in ${sourceLang} language and translate it to ${targetLang}. Return only the translated text.`;

        const requestBody = {
            system_instruction: {
                parts: [{
                    text: prompt
                }]
            },
            contents: {
                parts: [{
                    inlineData: {
                        mimeType: "image/png",
                        data: image
                    }
                }]
            },

            generationConfig: {
                temperature: TEMPERATURE,
                maxOutputTokens: MAX_TOKENS
            },
            safetySettings: [
                {
                    category: "HARM_CATEGORY_HARASSMENT",
                    threshold: "BLOCK_NONE"
                },
                {
                    category: "HARM_CATEGORY_HATE_SPEECH",
                    threshold: "BLOCK_NONE"
                },
                {
                    category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold: "BLOCK_NONE"
                },
                {
                    category: "HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold: "BLOCK_NONE"
                }
            ]
        };

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`API request failed with status: ${response.status}`);
        }

        const data = await response.json();
        const translatedText = data.candidates?.[0]?.content?.parts?.[0]?.text?.trim();
        if (!translatedText) {
            throw new Error('No translated text found in response');
        }
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
