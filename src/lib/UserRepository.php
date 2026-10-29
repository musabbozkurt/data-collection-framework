<?php

declare(strict_types=1);

namespace App;

use PDO;

final class UserRepository
{
    public function __construct(private PDO $pdo)
    {
    }

    public function emailExists(string $email): bool
    {
        return $this->findByEmail($email) !== null;
    }

    public function findByEmail(string $email): ?array
    {
        $statement = $this->pdo->prepare('SELECT id, name, email, password_hash FROM users WHERE email = :email');
        $statement->execute(['email' => $email]);
        return $statement->fetch() ?: null;
    }

    /** The first account that was created; only it may change the settings. */
    public function firstUserId(): ?int
    {
        $id = $this->pdo->query('SELECT MIN(id) FROM users')->fetchColumn();
        return $id === null || $id === false ? null : (int)$id;
    }

    public function create(string $name, string $email, string $password): void
    {
        $statement = $this->pdo->prepare(
            'INSERT INTO users (name, email, password_hash) VALUES (:name, :email, :hash)'
        );
        $statement->execute([
            'name' => $name,
            'email' => $email,
            'hash' => password_hash($password, PASSWORD_DEFAULT),
        ]);
    }
}
