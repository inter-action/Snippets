
// create a custom error Object 
function ModelError(status, message) {
  if (!(this instanceof ModelError)) return new ModelError(status, message);
  Object.setPrototypeOf(this.constructor.prototype, Error.prototype);
  // capture current stack trace to this error
  // view nodejs doc for more info
  Error.captureStackTrace(this, this.constructor);
  this.name = this.constructor.name;
  this.status = status;
  this.message = message;
}



