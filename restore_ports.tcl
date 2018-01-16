#!/bin/sh
# -*- coding: utf-8; mode: tcl; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- vim:fenc=utf-8:ft=tcl:et:sw=4:ts=4:sts=4
# \
if /usr/bin/which -s port-tclsh; then exec port-tclsh "$0" -i `which port-tclsh` "$@"; else exec /usr/bin/tclsh "$0" -i /usr/bin/tclsh "$@"; fi
#
# Install a list of ports given in the form produced by 'port installed', in
# correct dependency order so as to preserve the selected variants.
#
# Todo:
# Handle conflicting ports somehow
# Once "good enough", integrate into port


set MY_VERSION 0.1

proc printUsage {} {
   puts "Usage: $::argv0 \[-hV\] \[-p macports-prefix\] \[filename\]"
   puts "   -h   This help"
   puts "   -p   Use a different MacPorts prefix"
   puts "        (defaults to /opt/local)"
   puts "   -V   show version and MacPorts version being used"
}


proc dependenciesForPort {portName variantInfo} {
   set dependencyList [list]
   set portSearchResult [mportlookup $portName]
   if {[llength $portSearchResult] < 2} {
      ui_warn "Skipping $portName (not in the ports tree)"
      return $dependencyList
   }
   array set portInfo [lindex $portSearchResult 1]
   if {[catch {set mport [mportopen $portInfo(porturl) [list subport $portInfo(name)] $variantInfo]} result]} {
      global errorInfo
      puts stderr "$errorInfo"
      return -code error "Unable to open port '$portName': $result"
   }
   array unset portInfo
   array set portInfo [mportinfo $mport]
   mportclose $mport
   foreach dependencyType {depends_fetch depends_extract depends_build depends_lib depends_run} {
      if {[info exists portInfo($dependencyType)] && [string length $portInfo($dependencyType)] > 0} {
         foreach dependency $portInfo($dependencyType) {
            lappend dependencyList [lindex [split $dependency :] end]
         }
      }
   }

   return $dependencyList
}

proc sort_ports {portList} {
    array set port_installed {}
    array set port_deps {}
    array set port_in_list {}
    
    set newList [list]
    foreach port $portList {
        set name [lindex $port 0]
        #ui_msg "name = $name"
        set version [lindex $port 1]
        set variants ""

        if {[regexp {^@([^+]+?)(_(\d+)(([-+][^-+]+)*))?$} $version - - - - variantstr] && [info exists variantstr]} {
            while 1 {
                set nextplus [string last + $variantstr]
                set nextminus [string last - $variantstr]
                if {$nextplus > $nextminus} {
                    set next $nextplus
                    set sign +
                } else {
                    set next $nextminus
                    set sign -
                }
                if {$next == -1} {
                    break
                }
                set v [string range $variantstr [expr $next + 1] end]
                lappend variants $v $sign
                set variantstr [string range $variantstr 0 [expr $next - 1]]
            }
        }
        #ui_msg "variants = $variants"
        set active 0
        if {[llength $port] > 2 && [lindex $port 2] == "(active)"} {
            set active 1
        }
        #ui_msg "active = $active"

        if {![info exists port_in_list($name)]} {
            set port_in_list($name) 1
            set port_installed($name) 0
        } else {
            incr port_in_list($name)
        }
        if {![info exists port_deps(${name},${variants})]} {
            set port_deps(${name},${variants}) [dependenciesForPort $name $variants]
        }
        lappend newList [list $active $name $variants]
    }

    set operationList [list]
    while {[llength $newList] > 0} {
        set oldLen [llength $newList]
        foreach port $newList {
            foreach {active name variants} $port break
            # ensure active versions are installed after inactive versions,
            # since installing will also activate and we don't want to
            # displace the active version
            if {$active && $port_installed($name) < ($port_in_list($name) - 1)} {
                continue
            }
            set installable 1
            foreach dep $port_deps(${name},${variants}) {
                # XXX maybe check dep is active here?
                if {[info exists port_installed($dep)] && $port_installed($dep) == 0} {
                    set installable 0
                    break
                }
            }
            if {$installable} {
                lappend operationList [list $name $variants $active]
                incr port_installed($name)
                set index [lsearch $newList [list $active $name $variants]]
                #ui_msg "deleting \"[list $active $name $variants]\" from list"
                #ui_msg "list with element: $newList"
                set newList [lreplace $newList $index $index]
                #ui_msg "list without element: $newList"
            }
        }
        if {[llength $newList] == $oldLen} {
            ui_error "we appear to be stuck, exiting..."
            return -code error "infinite loop"
        }
    }
    
    return $operationList
}

proc install_ports {operationList} {
    foreach op $operationList {
        set name [string trim [lindex $op 0]]
        set variations [lindex $op 1]
        set active [lindex $op 2]

        if {!$active} {
            set install_target install
        } else {
            set install_target activate
        }

        if {[catch {set res [mportlookup $name]} result]} {
            global errorInfo
            ui_debug "$errorInfo"
            return -code error "lookup of portname $name failed: $result"
        }
        if {[llength $res] < 2} {
            # not in the index, but we already warned about that earlier
            continue
        }
        array unset portinfo
        array set portinfo [lindex $res 1]
        set porturl $portinfo(porturl)
        
        # XXX should explicitly turn off default variants that don't appear in the list
        
        if {[catch {set workername [mportopen $porturl [list subport $portinfo(name)] $variations]} result]} {
            global errorInfo
            puts stderr "$errorInfo"
            return -code error "Unable to open port '$name': $result"
        }
        if {[catch {set result [mportexec $workername $install_target]} result]} {
            global errorInfo
            mportclose $workername
            ui_msg "$errorInfo"
            return -code error "Unable to execute target 'install' for port '$name': $result"
        } else {
            mportclose $workername
        }
        
        # XXX some ports may be reactivated to fulfil dependencies - check again at the end?
    }
}

proc read_portlist {filename} {
    if {$filename == "-"} {
        set infile stdin
    } else {
        set infile [open $filename r]
    }
    set data [read -nonewline $infile]
    set portList [split $data \n]
    close $infile
    if {[lindex $portList 0] == "The following ports are currently installed:"} {
        set portList [lrange $portList 1 end]
    }
    return $portList
}

# Begin

set macportsPrefix /opt/local
set showVersion 0
array set ui_options {}

set origArgv $::argv
while {[string index [lindex $::argv 0] 0] == "-" } {
   switch [string range [lindex $::argv 0] 1 end] {
      h {
         printUsage
         exit 0
      }
      i {
         set interp_path [lindex $::argv 1]
         set ::argv [lrange $::argv 1 end]
      }
      p {
         if {[llength $::argv] < 2} {
            puts stderr "-p needs a path"
            printUsage
            exit 1
         }
         set macportsPrefix [lindex $::argv 1]
         set ::argv [lrange $::argv 1 end]
         set userPrefix 1
      }
      V {
         set showVersion 1
      }
      v {
        set ui_options(ports_verbose) yes
      }
      default {
         puts stderr "Unknown option [lindex $::argv 0]"
         printUsage
         exit 1
      }
   }
   set ::argv [lrange $::argv 1 end]
}

# check that default prefix exists
if {![info exists userPrefix] && ![file isdirectory $macportsPrefix]} {
    error "prefix '$macportsPrefix' does not exist; maybe you need to use the -p option?"
}

if {[info exists interp_path]} {
    set prefixFromInterp [file dirname [file dirname $interp_path]]
} else {
    # presumably the user ran '/some/prefix/bin/port-tclsh restore_ports.tcl'
    set prefixFromInterp ""
    if {[info exists userPrefix]} {
        error "the -p option cannot be used when running with an explicit interpreter (e.g. 'port-tclsh restore_ports.tcl') - run just './restore_ports.tcl' instead."
    }
}
# make sure we're running in the port-tclsh associated with the correct prefix
if {$prefixFromInterp ne "" && $prefixFromInterp ne $macportsPrefix} {
    if {[file executable ${macportsPrefix}/bin/port-tclsh]} {
        exec ${macportsPrefix}/bin/port-tclsh $argv0 -i ${macportsPrefix}/bin/port-tclsh {*}[lrange $origArgv 2 end] <@stdin >@stdout 2>@stderr
        exit 0
    } else {
        error "prefix '$macportsPrefix' does not appear to have a working port-tclsh"
    }
}

package require macports
package require Pextlib 1.0
umask 022
mportinit ui_options

if {$showVersion} {
   puts "Version $MY_VERSION"
   puts "MacPorts version [macports::version]"
   exit 0
}

if {[llength $::argv] == 0} {
   set filename "-"
} else {
    set filename [lindex $::argv 0]
}
set portList [read_portlist $filename]
#ui_msg "portlist = $portList"

set operationList [sort_ports $portList]

install_ports $operationList
