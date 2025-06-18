import { useRef, useState } from "react";
import { Box, HStack, VStack, Button, Input, Text } from "@chakra-ui/react";
import { Editor } from "@monaco-editor/react";
import LanguageSelector from "./LanguageSelector";
import { CODE_SNIPPETS } from "../constants";
import Output from "./Output";
import { toaster } from "./ui/Toaster";

const CodeEditor = () => {
  const editorRef = useRef();
  const [value, setValue] = useState("");
  const [language, setLanguage] = useState("javascript");
  const [task, setTask] = useState("");

  const onMount = (editor) => {
    editorRef.current = editor;
    editor.focus();
  };

  const onSelect = (language) => {
    setLanguage(language);
    setValue(CODE_SNIPPETS[language]);
  };

  return (
    <Box>
      <VStack spacing={4} align="stretch">
        <Box mb={4}>
          <Text mb={2} fontSize="lg">Task Description:</Text>
          <Input
            placeholder="Enter your task description here..."
            value={task}
            onChange={(e) => setTask(e.target.value)}
            bg="gray.800"
            color="white"
            _placeholder={{ color: 'gray.500' }}
          />
        </Box>
        <HStack spacing={4}>
          <Box w="50%">
            <HStack mb={4}>
              <LanguageSelector language={language} onSelect={onSelect} />
            </HStack>
            <Editor
              options={{
                minimap: {
                  enabled: false,
                },
              }}
              height="75vh"
              theme="vs-dark"
              language={language}
              defaultValue={CODE_SNIPPETS[language]}
              onMount={onMount}
              value={value}
              onChange={(value) => setValue(value)}
            />
          </Box>
          <VStack w="50%" spacing={4}>
            <Output editorRef={editorRef} language={language} task={task} />
          </VStack>
        </HStack>
      </VStack>
    </Box>
  );
};

export default CodeEditor;