<?php

declare(strict_types=1);

namespace App;

/** Shared HTTP plumbing (curl) of the REST and GraphQL clients. */
abstract class HttpClient extends PythonServerClient
{
    public function __construct(protected string $baseUrl, string $token = '')
    {
        parent::__construct($token);
    }

    /**
     * POSTs a JSON body and returns the decoded JSON answer, or an error reply string.
     *
     * @param string $path
     * @param array $body
     * @param int $readTimeout
     * @return array{0: mixed, 1: ?string} [decoded body, error message]
     * @throws \JsonException
     */
    protected function post(string $path, array $body, int $readTimeout): array
    {
        $headers = ['Content-Type: application/json', 'Accept: application/json'];
        if ($this->token !== '') {
            $headers[] = 'Authorization: Bearer ' . $this->token;
        }
        $curl = curl_init(rtrim($this->baseUrl, '/') . $path);
        curl_setopt_array($curl, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($body, JSON_THROW_ON_ERROR),
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => $this->connectTimeout,
            CURLOPT_TIMEOUT => $readTimeout,
            CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        ]);
        $raw = curl_exec($curl);
        $status = (int)curl_getinfo($curl, CURLINFO_RESPONSE_CODE);
        $errno = curl_errno($curl);
        $error = curl_error($curl);
        curl_close($curl);

        return self::decode($raw, $status, $errno, $error);
    }

    /** @return array{0: mixed, 1: ?string} */
    private static function decode(string|bool $raw, int $status, int $errno, string $error): array
    {
        $result = [json_decode(is_string($raw) ? $raw : '', true), null];
        if ($errno === CURLE_OPERATION_TIMEDOUT) {
            $result = [['ok' => true, 'message' => self::LONG_RUNNING], null];
        } elseif ($raw === false) {
            $result = [null, "Cannot reach the Python server ({$error})"];
        } elseif ($status === 401) {
            $result = [null, 'Unauthorized: check PY_SERVER_TOKEN'];
        }
        return $result;
    }
}
