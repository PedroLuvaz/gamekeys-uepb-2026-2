import { useId, useState } from "react";
import type { Jogo } from "./api";

const paletas = [
  ["#1c254c", "#a06bf4", "#f3a6e6"],
  ["#153e46", "#39a5a1", "#d6f2a4"],
  ["#341e37", "#d47560", "#ffc77d"],
  ["#182d4c", "#428aa8", "#a4e0f2"],
  ["#32334e", "#8875ba", "#f4dd97"],
  ["#303423", "#899b59", "#edeca5"],
];

export default function ArteJogo({
  jogo,
  grande = false,
}: {
  jogo: Jogo;
  grande?: boolean;
}) {
  const uid = useId();
  const [falhou, setFalhou] = useState(false);
  const variante =
    [...jogo.nome].reduce((soma, letra) => soma + letra.charCodeAt(0), 0) % 6;
  const [fundo, meio, luz] = paletas[variante];

  return (
    <div className={`arte-jogo${grande ? " arte-grande" : ""}`}>
      {jogo.capa_url && !falhou ? (
        <img
          src={jogo.capa_url}
          alt={`Capa de ${jogo.nome}`}
          loading="lazy"
          onError={() => setFalhou(true)}
        />
      ) : (
        <>
          <svg
            viewBox="0 0 480 300"
            preserveAspectRatio="xMidYMid slice"
            aria-hidden="true"
          >
            <defs>
              <linearGradient id={`${uid}-ceu`} x2="0.7" y2="1">
                <stop stopColor={fundo} />
                <stop offset="1" stopColor={meio} />
              </linearGradient>
              <linearGradient id={`${uid}-chao`} x2="0" y2="1">
                <stop stopColor={meio} />
                <stop offset="1" stopColor={fundo} />
              </linearGradient>
            </defs>
            <rect width="480" height="300" fill={`url(#${uid}-ceu)`} />
            <circle
              cx={variante % 2 ? 330 : 150}
              cy="88"
              r="49"
              fill={luz}
              opacity=".8"
            />
            <circle cx="380" cy="40" r="2" fill="white" opacity=".7" />
            <circle cx="90" cy="60" r="2" fill="white" opacity=".7" />
            <circle cx="240" cy="30" r="1" fill="white" opacity=".7" />
            {variante % 3 === 0 ? (
              <>
                <path
                  d="M0 240V120h35v-35h40v155h23V150h45v90h25V90h60v150h40V130h48v110h15V65h52v175h20V110h55v130z"
                  fill={fundo}
                  opacity=".85"
                />
                <path
                  d="M40 110h15m-15 20h15m125-15h22m-22 20h22m-22 20h22m142-57h18m-18 20h18m-18 20h18"
                  stroke={luz}
                  strokeWidth="4"
                  opacity=".7"
                />
                <path d="M170 300 240 196 310 300" fill={meio} />
                <path d="M236 300 240 224 244 300" fill={luz} opacity=".7" />
              </>
            ) : (
              <>
                <path
                  d="M0 235 100 97 196 218 280 123 480 250V300H0z"
                  fill={meio}
                  opacity=".7"
                />
                <path
                  d="m0 280 130-114 98 92 80-113 172 121v34H0z"
                  fill={`url(#${uid}-chao)`}
                />
                <path
                  d="m283 300 20-59 20 59m-64-116 19-71 20 71m-208 44 25-77 27 77"
                  fill={fundo}
                />
                <path
                  d="M0 290 124 256 200 276 320 235 480 282v18H0z"
                  fill={fundo}
                />
              </>
            )}
            <path d="M0 299h480" stroke={luz} opacity=".25" />
          </svg>
          <span className="arte-legenda">Arte ilustrativa</span>
        </>
      )}
    </div>
  );
}
