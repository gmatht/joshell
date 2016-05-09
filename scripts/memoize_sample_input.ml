module Droid = struct
        type t = string
        let  empty = ""
        let  beep x = x ^ " notdroids"
        let  boop x = x ^ " lookingfor"
	let  cat x y = print_string "catting\n" ; x ^ y 
        let  len x = String.length x
	let  println x = print_string (x ^ "\n")
        let  words = [beep empty; boop empty]

	let equal = (=)
	let hash  = Hashtbl.hash
	
end

(* MEMOIZE MODULE Droid *)

let testbeep = (Droid.beep (Droid.beep Droid.empty))
let testboop = (Droid.boop Droid.empty)
let _ = Droid.println ((Droid.cat testbeep testboop))
let _ = Droid.println ((Droid.cat testbeep testboop))
let _ = Droid.println ((Droid.cat testbeep testboop))
let _ = Droid.println ((Droid.cat testbeep testboop))
let _ = List.iter Droid.println Droid.words
;;
