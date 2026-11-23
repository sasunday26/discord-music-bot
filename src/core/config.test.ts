import { describe, expect, it } from "vitest";
import { parseBotConfig, parseRegisterCommandsConfig } from "./config.ts";
import { err, ok } from "./result.ts";

const validEnv = {
  DISCORD_BOT_TOKEN: "token",
  LAVALINK_URI: "http://localhost:2333",
  LAVALINK_PASSWORD: "youshallnotpass",
  OUTRO_VIDEO_URL: "https://www.youtube.com/watch?v=abc",
  OUTRO_VIDEO_TIMESTAMP_MS: "12345",
  LEAVE_EMPTY_CHANNEL_AFTER_SEC: "300",
};

const requiredVariables = Object.keys(validEnv);

describe("parseBotConfig", () => {
  it("parses a valid env", () => {
    expect(parseBotConfig(validEnv)).toEqual(
      ok({
        discord: { botToken: "token" },
        lavalink: {
          url: "localhost:2333",
          secure: false,
          password: "youshallnotpass",
        },
        outro: {
          url: "https://www.youtube.com/watch?v=abc",
          timestampMs: 12345,
        },
        log: { level: "info" },
        leaveEmptyChannelAfterSec: 300,
      }),
    );
  });

  it.each([
    ["http://127.0.0.1:2333", { url: "127.0.0.1:2333", secure: false }],
    ["https://lavalink.example.com", { url: "lavalink.example.com", secure: true }],
    ["https://lavalink.example.com:443", { url: "lavalink.example.com", secure: true }],
    ["https://lavalink.example.com:8443", { url: "lavalink.example.com:8443", secure: true }],
  ])("parses LAVALINK_URI %s", (uri, expected) => {
    const config = parseBotConfig({ ...validEnv, LAVALINK_URI: uri });
    expect(config.isOk() && config.value.lavalink).toEqual({
      ...expected,
      password: "youshallnotpass",
    });
  });

  it.each(["debug", "info", "warn", "error"])("accepts LOG_LEVEL %s", (level) => {
    const config = parseBotConfig({ ...validEnv, LOG_LEVEL: level });
    expect(config.isOk() && config.value.log.level).toBe(level);
  });

  it("defaults an empty LOG_LEVEL to info", () => {
    const config = parseBotConfig({ ...validEnv, LOG_LEVEL: "" });
    expect(config.isOk() && config.value.log.level).toBe("info");
  });

  it.each(requiredVariables)("reports missing %s", (variable) => {
    expect(parseBotConfig({ ...validEnv, [variable]: undefined })).toEqual(
      err({ variable, problem: "missing" }),
    );
  });

  it.each(requiredVariables)("treats empty %s as missing", (variable) => {
    expect(parseBotConfig({ ...validEnv, [variable]: "" })).toEqual(
      err({ variable, problem: "missing" }),
    );
  });

  it.each([
    ["LAVALINK_URI", "localhost:2333"],
    ["LAVALINK_URI", "ftp://localhost:2333"],
    ["LAVALINK_URI", "http://localhost:2333/v4"],
    ["LAVALINK_URI", "http://localhost:2333?x=1"],
    ["OUTRO_VIDEO_URL", "not a url"],
    ["OUTRO_VIDEO_URL", "ftp://example.com/video"],
    ["OUTRO_VIDEO_TIMESTAMP_MS", "abc"],
    ["OUTRO_VIDEO_TIMESTAMP_MS", "0"],
    ["OUTRO_VIDEO_TIMESTAMP_MS", "-5"],
    ["OUTRO_VIDEO_TIMESTAMP_MS", "1.5"],
    ["OUTRO_VIDEO_TIMESTAMP_MS", "1e3"],
    ["OUTRO_VIDEO_TIMESTAMP_MS", " 12 "],
    ["OUTRO_VIDEO_TIMESTAMP_MS", "0x10"],
    ["LEAVE_EMPTY_CHANNEL_AFTER_SEC", "99999999999999999999"],
    ["LOG_LEVEL", "verbose"],
    ["LOG_LEVEL", "INFO"],
  ])("rejects %s=%j", (variable, value) => {
    expect(parseBotConfig({ ...validEnv, [variable]: value })).toEqual(
      err({ variable, problem: "invalid" }),
    );
  });

  it("reports the first error in declaration order", () => {
    expect(parseBotConfig({})).toEqual(
      err({ variable: "DISCORD_BOT_TOKEN", problem: "missing" }),
    );
  });
});

describe("parseRegisterCommandsConfig", () => {
  const registerEnv = {
    DISCORD_BOT_TOKEN: "token",
    DISCORD_CLIENT_ID: "123456789012345678",
  };

  it("parses a valid env without bot-only variables", () => {
    expect(parseRegisterCommandsConfig(registerEnv)).toEqual(
      ok({
        discord: { botToken: "token", clientId: "123456789012345678" },
      }),
    );
  });

  it.each(Object.keys(registerEnv))("reports missing %s", (variable) => {
    expect(
      parseRegisterCommandsConfig({ ...registerEnv, [variable]: undefined }),
    ).toEqual(err({ variable, problem: "missing" }));
  });
});
