/*
 * This file is part of Finn.
 *
 * Copyright (c) 2020 Jan de Visser <jan@finiandarcy.com>
 *
 * Finn is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Finn is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Finn.  If not, see <https://www.gnu.org/licenses/>.
 */

function Lookup(parentId, options) {
    this.field = options.name;
    this.ref = options.ref;
    this.query = options.query;
    this.display = options.display;
    this.href = options.href;

    this.onInput = function(e) {
        const val = this.input.value;
        if (val === "") {
            return;
        }
        const url = this.url(val);
        fetch(url)
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                for (let child = this.dataList.lastElementChild; child; child = this.dataList.lastElementChild) {
                    this.dataList.removeChild(child);
                }
                if (data.length) {
                    for (let i = 0, len = data.length; i < len; i++) {
                        const row = data[i];
                        const opt = document.createElement("option")
                        opt.value = this.value(row);
                        opt.text = this.text(row);
                        this.dataList.appendChild(opt);
                    }
                }
            });
    };

    this.onChange = function(e) {
        const val = this.input.value;
        if (val === "") {
            this.data.value = "0";
            return;
        }
        for (let child = this.dataList.firstElementChild; child; child = child.nextElementSibling) {
            if (child.value === val) {
                this.input.value = child.text;
                this.data.value = child.value;
                break;
            }
        }
    };

    this.url = function(value) {
        return `/json/${this.ref["_kind"]}?${this.ref.query}=${encodeURIComponent(value)}`;
    };

    this.value = function(row) {
        return (row && row[0]) ? row[0].Ident : 0;
    };

    this.text = function(row) {
        if (row && row[0]) {
            const e = row[0];
            const p = (row.length > 1) ? row[1] : null;
            return eval(this.display);
        } else {
            return "";
        }
    };

    const parent = document.getElementById(parentId);
    if (!parent) {
        return;
    }

    this.dataList = document.createElement("datalist");
    this.dataList.id = `${this.field}-Datalist`;
    parent.appendChild(this.dataList);

    this.input = document.createElement("input");
    this.input.id = `${this.name}-Input`;
    this.input.type = "text";
    this.input.className = "form-control";
    this.input.setAttribute("list",`${this.field}-Datalist`);
    this.input.value = this.text([this.ref]);
    this.input.oninput = this.onInput.bind(this);
    this.input.onchange = this.onChange.bind(this);
    parent.appendChild(this.input);

    this.data = document.createElement("input");
    this.data.id = `${this.field}-Data`;
    this.data.name = this.field;
    this.data.type = "hidden";
    this.data.value = this.value([this.ref]);
    parent.appendChild(this.data);
}
