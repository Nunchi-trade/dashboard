import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { Inter, DM_Serif_Display } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });
const dmSerif = DM_Serif_Display({ weight: "400", subsets: ["latin"] });

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <style jsx global>{`
        :root {
          --font-inter: ${inter.style.fontFamily};
          --font-dm-serif: ${dmSerif.style.fontFamily};
        }
        .font-serif {
          font-family: ${dmSerif.style.fontFamily}, Georgia, serif;
        }
      `}</style>
      <main className={inter.className}>
        <Component {...pageProps} />
      </main>
    </>
  );
}
