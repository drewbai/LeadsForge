import type { ReactNode } from "react";

type AboutCardProps = {
  title: string;
  children: ReactNode;
};

export default function AboutCard(props: AboutCardProps) {
  return (
    <section className="card aboutCard">
      <h2 className="aboutCardTitle">{props.title}</h2>
      {props.children}
    </section>
  );
}
