# Injeção defensiva de links nos arquivos README (PT-BR e EN-US)
# Nenhuma dependência de scraping; recebe apenas estruturas de links validadas.

import os
import re
from typing import List, Dict
from datetime import datetime


class ReadmeDefensiveLinkInjectorEngine:
    """Injetor defensivo de índices automáticos para conteúdos do Intelligence Hub."""

    def __init__(
        self,
        readme_portuguese_path_string: str = "README.md",
        readme_english_path_string: str = "README-us.md",
        github_pages_base_url_string: str = (
            "https://fatal1tybarucco.github.io/Salesforce-WebDev/"
        ),
    ) -> None:
        self.readme_portuguese_path_string: str = readme_portuguese_path_string
        self.readme_english_path_string: str = readme_english_path_string
        self.github_pages_base_url_string: str = github_pages_base_url_string
        if not self.readme_portuguese_path_string or not self.readme_english_path_string:
            raise ValueError("Caminhos de README não podem ser nulos.")

    def inject_intelligence_index_into_readme_files(
        self,
        release_identifier_string: str,
        generated_link_entries: List[Dict[str, str]],
    ) -> None:
        """Injeta índices defensivos nos dois READMEs."""
        for file_path_string in [
            self.readme_portuguese_path_string,
            self.readme_english_path_string,
        ]:
            if not os.path.exists(file_path_string):
                print(f"[DEFENSIVO] Arquivo não encontrado: {file_path_string}")
                continue
            try:
                with open(file_path_string, "r", encoding="utf-8") as file_handler:
                    file_content_string = file_handler.read()
            except Exception as exception_instance:
                print(
                    f"[DEFENSIVO] Falha ao ler arquivo: {file_path_string} — {exception_instance}"
                )
                continue

            index_header_text = (
                f"\n<!-- Salesforce Intelligence Hub — Release {release_identifier_string} -->\n"
                f"## Índice Automático — Intelligence Hub (Release {release_identifier_string})\n"
            )
            for link_entry in generated_link_entries:
                index_header_text += f"- [{link_entry.get('label', 'Link')}]({self.github_pages_base_url_string}{link_entry.get('relative_path', '')})\n"
            index_header_text += (
                f"*Atualizado automaticamente em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            )

            # Defensivo: não substitui se já existe o mesmo release_identifier no comentário
            if f"Release {release_identifier_string}" in file_content_string:
                # Atualiza ao invés de duplicar (substitui seção existente defensivamente)
                try:
                    updated_content_string = re.sub(
                        r"<!-- Salesforce Intelligence Hub — Release \d+ -->.*?\*Atualizado automaticamente em: .*?\*",
                        index_header_text.strip(),
                        file_content_string,
                        flags=re.DOTALL,
                    )
                    file_content_string = updated_content_string
                except Exception:
                    file_content_string += "\n" + index_header_text
            else:
                file_content_string += "\n" + index_header_text

            try:
                with open(file_path_string, "w", encoding="utf-8") as file_writer:
                    file_writer.write(file_content_string)
            except Exception as exception_instance:
                print(
                    f"[DEFENSIVO] Falha ao escrever arquivo: {file_path_string} — {exception_instance}"
                )
