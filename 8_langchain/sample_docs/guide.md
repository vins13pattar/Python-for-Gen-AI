# Introduction

LangChain is a framework for building LLM-powered applications.

## Core Concepts

LCEL (LangChain Expression Language) lets you compose chains using the pipe operator. It supports streaming, batching, and async.

## Document Loaders

Document loaders ingest data from PDFs, web pages, databases, and more. Each loader returns a list of Document objects with page_content and metadata.

## Text Splitters

Text splitters divide large documents into smaller chunks that fit within an LLM context window. Common splitters include RecursiveCharacterTextSplitter and TokenTextSplitter.