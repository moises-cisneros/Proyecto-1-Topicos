/// <reference types="vite/client" />

declare module '@resources/*.json' {
  const value: any;
  export default value;
}

declare module '@resources/*.csv?raw' {
  const content: string;
  export default content;
}

declare module '@resources/*.csv' {
  const content: string;
  export default content;
}
