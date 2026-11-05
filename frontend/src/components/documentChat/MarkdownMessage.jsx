const inlinePatterns = [
  {
    regex: /`([^`]+)`/g,
    render: (content, key) => (
      <code
        key={key}
        className="rounded bg-gray-200 px-1 py-0.5 font-mono text-[0.8125rem] text-gray-900 dark:bg-gray-800 dark:text-gray-100"
      >
        {content}
      </code>
    ),
  },
  {
    regex: /\*\*([^*]+)\*\*/g,
    render: (content, key) => <strong key={key}>{content}</strong>,
  },
  {
    regex: /\*([^*]+)\*/g,
    render: (content, key) => <em key={key}>{content}</em>,
  },
  {
    regex: /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    render: (content, key, href) => (
      <a
        key={key}
        href={href}
        target="_blank"
        rel="noreferrer"
        className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-800 dark:text-purple-300 dark:hover:text-purple-200"
      >
        {content}
      </a>
    ),
  },
];

function renderInline(text) {
  let parts = [text];

  inlinePatterns.forEach(({ regex, render }) => {
    const nextParts = [];

    parts.forEach((part) => {
      if (typeof part !== "string") {
        nextParts.push(part);
        return;
      }

      let lastIndex = 0;
      regex.lastIndex = 0;
      const matches = [...part.matchAll(regex)];

      if (matches.length === 0) {
        nextParts.push(part);
        return;
      }

      matches.forEach((match, index) => {
        if (match.index > lastIndex) {
          nextParts.push(part.slice(lastIndex, match.index));
        }

        nextParts.push(
          render(
            match[1],
            `${match.index}-${index}-${match[0]}`,
            match[2],
          ),
        );
        lastIndex = match.index + match[0].length;
      });

      if (lastIndex < part.length) {
        nextParts.push(part.slice(lastIndex));
      }
    });

    parts = nextParts;
  });

  return parts;
}

function flushParagraph(blocks, paragraphLines) {
  if (paragraphLines.length === 0) {
    return;
  }

  blocks.push({ type: "paragraph", text: paragraphLines.join(" ") });
  paragraphLines.length = 0;
}

function parseMarkdown(markdown) {
  const lines = String(markdown || "").split("\n");
  const blocks = [];
  const paragraphLines = [];
  let codeBlock = null;
  let listBlock = null;

  const flushList = () => {
    if (listBlock) {
      blocks.push(listBlock);
      listBlock = null;
    }
  };

  lines.forEach((line) => {
    const codeFence = line.match(/^```\s*([^`]*)$/);

    if (codeFence) {
      if (codeBlock) {
        blocks.push(codeBlock);
        codeBlock = null;
      } else {
        flushParagraph(blocks, paragraphLines);
        flushList();
        codeBlock = {
          type: "code",
          language: codeFence[1]?.trim(),
          text: "",
        };
      }
      return;
    }

    if (codeBlock) {
      codeBlock.text += `${codeBlock.text ? "\n" : ""}${line}`;
      return;
    }

    if (!line.trim()) {
      flushParagraph(blocks, paragraphLines);
      flushList();
      return;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph(blocks, paragraphLines);
      flushList();
      blocks.push({
        type: "heading",
        level: heading[1].length,
        text: heading[2].trim(),
      });
      return;
    }

    const quote = line.match(/^>\s?(.+)$/);
    if (quote) {
      flushParagraph(blocks, paragraphLines);
      flushList();
      blocks.push({ type: "quote", text: quote[1].trim() });
      return;
    }

    const unorderedItem = line.match(/^[-*]\s+(.+)$/);
    const orderedItem = line.match(/^\d+[.)]\s+(.+)$/);
    if (unorderedItem || orderedItem) {
      flushParagraph(blocks, paragraphLines);
      const type = orderedItem ? "ordered-list" : "unordered-list";
      const text = (orderedItem || unorderedItem)[1].trim();

      if (!listBlock || listBlock.type !== type) {
        flushList();
        listBlock = { type, items: [] };
      }

      listBlock.items.push(text);
      return;
    }

    flushList();
    paragraphLines.push(line.trim());
  });

  if (codeBlock) {
    blocks.push(codeBlock);
  }
  flushParagraph(blocks, paragraphLines);
  flushList();

  return blocks;
}

export default function MarkdownMessage({ text }) {
  const blocks = parseMarkdown(text);

  return (
    <div className="space-y-2 text-sm leading-5 text-gray-800 dark:text-gray-100">
      {blocks.map((block, index) => {
        if (block.type === "heading") {
          const HeadingTag = block.level === 1 ? "h3" : block.level === 2 ? "h4" : "h5";
          return (
            <HeadingTag
              key={index}
              className="mt-1 font-semibold text-gray-950 first:mt-0 dark:text-white"
            >
              {renderInline(block.text)}
            </HeadingTag>
          );
        }

        if (block.type === "quote") {
          return (
            <blockquote
              key={index}
              className="border-l-2 border-purple-300 pl-3 text-gray-600 dark:border-purple-700 dark:text-gray-300"
            >
              {renderInline(block.text)}
            </blockquote>
          );
        }

        if (block.type === "code") {
          return (
            <pre
              key={index}
              className="overflow-x-auto rounded-md bg-gray-950 p-3 text-xs leading-5 text-gray-100"
            >
              <code>{block.text}</code>
            </pre>
          );
        }

        if (block.type === "unordered-list" || block.type === "ordered-list") {
          const ListTag = block.type === "ordered-list" ? "ol" : "ul";
          return (
            <ListTag
              key={index}
              className={`space-y-1 pl-5 ${
                block.type === "ordered-list" ? "list-decimal" : "list-disc"
              }`}
            >
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{renderInline(item)}</li>
              ))}
            </ListTag>
          );
        }

        return (
          <p key={index} className="whitespace-pre-wrap">
            {renderInline(block.text)}
          </p>
        );
      })}
    </div>
  );
}
