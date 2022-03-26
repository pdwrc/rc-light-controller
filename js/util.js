export function splitOnSpace(str) {
    const index = str.indexOf(" ");
    return [str.substr(0, index), str.substr(index + 1)];
}
