//! Prints the licenses of the syntax definitions two-face bundles, in the
//! format of `about.hbs`.

#![expect(clippy::print_stdout, reason = "printing the listing is what the example is for")]

fn main() {
    for license in two_face::acknowledgement::listing().for_syntaxes() {
        println!("{}", "=".repeat(80));
        println!("Syntax definition: {}", license.rel_path.display());
        println!();
        println!("{}", license.text.trim_end());
        println!();
    }
}
