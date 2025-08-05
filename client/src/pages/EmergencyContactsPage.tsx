import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Pencil, Trash2, PlusCircle, Search, ArrowLeft } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";
import { useAuth } from "@/context/AuthContext";
import { Badge } from "@/components/ui/badge";

const BASE_URL = "/api/v1"; // Use the proxy

interface Contact {
  id: number;
  name: string;
  relation: string;
  phone: string;
}

const contactSchema = yup.object().shape({
  name: yup.string().required("Name is required"),
  relation: yup.string().required("Relation is required"),
  phone: yup
    .string()
    .required("Phone number is required")
    .matches(
      /^\+?\d+$/,
      "Phone number must contain only digits and may start with +"
    ),
});

const EmergencyContactsPage: React.FC = () => {
  const { user } = useAuth();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editContact, setEditContact] = useState<Contact | null>(null);
  const [form, setForm] = useState<Omit<Contact, "id">>({
    name: "",
    relation: "",
    phone: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  // READ: Fetch contacts when the component mounts
  useEffect(() => {
    if (user) {
      setIsLoading(true);
      fetch(`${BASE_URL}/emergency-contacts/user/${user.id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch contacts");
          return res.json();
        })
        .then((data: Contact[]) => setContacts(data))
        .catch((err) => console.error("Fetch contacts error:", err))
        .finally(() => setIsLoading(false));
    }
  }, [user]);

  const openModal = (contact?: Contact) => {
    if (contact) {
      setEditContact(contact);
      setForm({
        name: contact.name,
        relation: contact.relation,
        phone: contact.phone,
      });
    } else {
      setEditContact(null);
      setForm({ name: "", relation: "", phone: "" });
    }
    setFormErrors({});
    setModalOpen(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name]) setFormErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSave = async () => {
    if (!user) return;

    try {
      await contactSchema.validate(form, { abortEarly: false });

      const method = editContact ? "PUT" : "POST";
      const endpoint = editContact
        ? `${BASE_URL}/emergency-contacts/${editContact.id}`
        : `${BASE_URL}/emergency-contacts/`;

      const payload = { ...form, user_id: user.id };

      const res = await fetch(endpoint, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errDetail = await res.json();
        throw new Error(errDetail.detail || "Failed to save contact");
      }

      if (editContact) {
        // UPDATE state
        const updatedContact = await res.json();
        setContacts((prev) =>
          prev.map((c) => (c.id === editContact.id ? updatedContact : c))
        );
      } else {
        // CREATE state
        const newContact = await res.json();
        setContacts((prev) => [...prev, newContact]);
      }
      setModalOpen(false);
    } catch (err: any) {
      if (err.inner) {
        const errors: Record<string, string> = {};
        err.inner.forEach((e: any) => {
          if (e.path) errors[e.path] = e.message;
        });
        setFormErrors(errors);
      } else {
        console.error("Save error:", err);
        setFormErrors({ form: err.message || "An unexpected error occurred." });
      }
    }
  };

  const handleDelete = async (id: number) => {
    if (!user) return;
    try {
      const res = await fetch(`${BASE_URL}/emergency-contacts/${id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errDetail = await res.json();
        throw new Error(errDetail.detail || "Failed to delete contact");
      }
      // DELETE from state
      setContacts((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      console.error("Delete error:", err);
    }
  };

  const filteredContacts = contacts.filter((c) => {
    const name = c.name?.toLowerCase() || "";
    const relation = c.relation?.toLowerCase() || "";
    const phone = c.phone || "";
    const term = searchTerm.toLowerCase();
    return (
      name.includes(term) || relation.includes(term) || phone.includes(term)
    );
  });

  const SkeletonLoader = () => (
    <div className="space-y-4 pt-4">
      {[...Array(3)].map((_, i) => (
        <Card key={i} className="p-4 animate-pulse">
          <div className="flex justify-between items-center">
            <div>
              <div className="h-6 w-32 bg-muted rounded mb-2"></div>
              <div className="h-4 w-24 bg-muted rounded mb-1"></div>
              <div className="h-4 w-28 bg-muted rounded"></div>
            </div>
            <div className="flex space-x-2">
              <div className="h-8 w-8 bg-muted rounded-md"></div>
              <div className="h-8 w-8 bg-muted rounded-md"></div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/home")}
            className="mr-4"
          >
            <ArrowLeft size={20} />
          </Button>
          Emergency Contacts
        </h2>
        <Button variant="outline" size="sm" onClick={() => openModal()}>
          <PlusCircle className="mr-2" size={16} /> Add Contact
        </Button>
      </div>

      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          size={16}
        />
        <Input
          placeholder="Search contacts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Contacts
            {!isLoading && (
              <Badge variant="secondary">{filteredContacts.length}</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            {isLoading ? (
              <SkeletonLoader />
            ) : contacts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No contacts found. Add one to get started.</p>
              </div>
            ) : filteredContacts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No matching contacts found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredContacts.map((contact) => (
                  <Card key={contact.id} className="p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-semibold text-lg">{contact.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {contact.relation}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {contact.phone}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openModal(contact)}
                        >
                          <Pencil size={16} />
                        </Button>
                        <Button
                          variant="destructive"
                          size="icon"
                          onClick={() => handleDelete(contact.id)}
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editContact ? "Edit Contact" : "Add Contact"}
            </DialogTitle>
            <DialogDescription>
              Fill in the emergency contact details.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div>
              <Input
                name="name"
                placeholder="Name"
                value={form.name}
                onChange={handleChange}
              />
              {formErrors.name && (
                <p className="text-xs text-red-500 mt-1">{formErrors.name}</p>
              )}
            </div>
            <div>
              <Input
                name="relation"
                placeholder="Relation"
                value={form.relation}
                onChange={handleChange}
              />
              {formErrors.relation && (
                <p className="text-xs text-red-500 mt-1">
                  {formErrors.relation}
                </p>
              )}
            </div>
            <div>
              <Input
                name="phone"
                placeholder="Phone"
                value={form.phone}
                onChange={handleChange}
              />
              {formErrors.phone && (
                <p className="text-xs text-red-500 mt-1">{formErrors.phone}</p>
              )}
            </div>
            {formErrors.form && (
              <p className="text-sm text-red-500 text-center">
                {formErrors.form}
              </p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              {editContact ? "Save Changes" : "Add Contact"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EmergencyContactsPage;
