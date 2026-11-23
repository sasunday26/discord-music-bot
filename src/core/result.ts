type Result<T, E> = Ok<T, E> | Err<T, E>;

const ok = <T>(value: T): Result<T, never> => new Ok(value);
const err = <const E>(error: E): Result<never, E> => new Err(error);

class Ok<T, E> {
  readonly kind = "ok";
  readonly value: T;

  constructor(value: T) {
    this.value = value;
  }

  isOk(): this is Ok<T, E> {
    return true;
  }

  isErr(): this is Err<T, E> {
    return false;
  }

  map<U>(f: (value: T) => U): Result<U, E> {
    return new Ok(f(this.value));
  }

  mapErr<F>(_f: (error: E) => F): Result<T, F> {
    return new Ok(this.value);
  }

  andThen<U, F>(f: (value: T) => Result<U, F>): Result<U, E | F> {
    return f(this.value);
  }
}

class Err<T, E> {
  readonly kind = "error";
  readonly error: E;

  constructor(error: E) {
    this.error = error;
  }

  isOk(): this is Ok<T, E> {
    return false;
  }

  isErr(): this is Err<T, E> {
    return true;
  }

  map<U>(_f: (value: T) => U): Result<U, E> {
    return new Err(this.error);
  }

  mapErr<F>(f: (error: E) => F): Result<T, F> {
    return new Err(f(this.error));
  }

  andThen<U, F>(_f: (value: T) => Result<U, F>): Result<U, E | F> {
    return new Err(this.error);
  }
}

export { err, ok, type Result };
